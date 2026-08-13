"""
Бизнес-логика для работы с записями, услугами и расписанием.

Предоставляет функции для бота и веб-календаря.
"""

from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import async_session
from app.models import Client, Service, Appointment, WorkingHours, BlockedTime


async def get_active_services():
    """
    Возвращает список активных услуг.

    Используется ботом для показа кнопок выбора услуги.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Service).where(Service.is_active)
        )
        return result.scalars().all()


async def get_available_dates():
    """
    Берёт ближайшие 14 дней, исключая выходные и возвращает список словарей с
    доступными датами.
    """
    async with async_session() as session:
        result = await session.execute(
            select(WorkingHours).where(WorkingHours.is_working)
        )
        working_days = {wh.day_of_week for wh in result.scalars().all()}

    dates = []
    today = date.today()

    for i in range(14):
        check_date = today + timedelta(days=i)
        if check_date.weekday() in working_days:
            dates.append({
                'label': check_date.strftime('%d.%m'),
                'value': check_date.isoformat()
            })

    return dates


async def get_service_by_id(service_id):
    """Возвращает услугу по ID или None, если услуги с таким ID нет."""
    async with async_session() as session:
        result = await session.execute(
            select(Service).where(Service.id == service_id)
        )
        return result.scalars().first()


def _is_slot_free(slot_start, slot_end, appointments, blocked_times):
    """Проверяет, не пересекается ли временной слот с занятым временем."""
    for app in appointments:
        if slot_start < app.end_time and slot_end > app.start_time:
            return False

    for block in blocked_times:
        if slot_start < block.end_time and slot_end > block.start_time:
            return False

    return True


async def get_available_slots(day, service_id):
    """
    Возвращает список свободного времени для записи на выбранную услугу в
    указанную дату.
    """
    async with async_session() as session:
        service_request = await session.execute(
            select(Service).where(Service.id == service_id)
        )
        service = service_request.scalars().first()
        if not service:
            return []

        duration = service.duration

        day_of_week = day.weekday()
        wh_request = await session.execute(
            select(WorkingHours).where(
                WorkingHours.day_of_week == day_of_week,
                WorkingHours.is_working
            )
        )
        working_hours = wh_request.scalars().first()
        if not working_hours:
            return []

        appointments_request = await session.execute(
            select(Appointment).where(
                Appointment.date == day,
                Appointment.status != 'отменена'
            )
        )
        appointments = appointments_request.scalars().all()

        blocked_request = await session.execute(
            select(BlockedTime).where(BlockedTime.date == day)
        )
        blocked_times = blocked_request.scalars().all()

        available = []

        current = datetime.combine(day, working_hours.start_time)
        end = datetime.combine(day, working_hours.end_time)

        while current + timedelta(minutes=duration) <= end:
            slot_start = current.time()
            slot_end = (current + timedelta(minutes=duration)).time()

            if _is_slot_free(
                slot_start, slot_end, appointments, blocked_times
            ):
                available.append(slot_start)

            current += timedelta(minutes=30)

        return available


async def create_appointment(telegram_id, service_id, day, start_time):
    """
    Создаёт новую запись, проверяя, что новый слот свободен. Если клиент не
    найден - создаёт его.

    Возвращает объект Appointment или None, если услуга не найдена или
    слот занят.
    """
    async with async_session() as session:
        client_request = await session.execute(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        client = client_request.scalars().first()

        if not client:
            client = Client(
                telegram_id=telegram_id,
                first_name='Клиент'
            )
            session.add(client)
            await session.flush()

        service_request = await session.execute(
            select(Service).where(Service.id == service_id)
        )
        service = service_request.scalars().first()
        if not service:
            return None

        start_dt = datetime.combine(day, start_time)
        end_dt = start_dt + timedelta(minutes=service.duration)
        end_time = end_dt.time()

        busy_request = await session.execute(
            select(Appointment).where(
                Appointment.date == day,
                Appointment.status != 'отменена'
            )
        )
        busy_appointments = busy_request.scalars().all()

        blocked_request = await session.execute(
            select(BlockedTime).where(BlockedTime.date == day)
        )
        blocked_times = blocked_request.scalars().all()

        if not _is_slot_free(
            start_time, end_time, busy_appointments, blocked_times
        ):
            return None

        appointment = Appointment(
            client_id=client.id,
            service_id=service.id,
            date=day,
            start_time=start_time,
            end_time=end_time,
            status='в ожидании'
        )

        session.add(appointment)
        await session.commit()

        return appointment


async def get_client_appointments(telegram_id):
    """Возвращает список активных записей клиента."""
    async with async_session() as session:
        client_request = await session.execute(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        client = client_request.scalars().first()
        if not client:
            return []

        result = await session.execute(
            select(Appointment).options(joinedload(Appointment.service)).where(
                Appointment.client_id == client.id,
                Appointment.status != 'отменена'
            ).order_by(Appointment.date, Appointment.start_time)
        )

        return result.unique().scalars().all()


async def cancel_appointment(appointment_id, telegram_id=None):
    """
    Отменяет запись.

    Если передан telegram_id - проверяет, что запись принадлежит клиенту.
    Если telegram_id не передан - отмена от имени мастера без проверки.

    Возвращает True - если запись отменена, False - если не найден клиент,
    не найдена запись, она уже удалена или принадлежит другому клиенту.
    """
    async with async_session() as session:
        conditions = [
            Appointment.id == appointment_id,
            Appointment.status != 'отменена'
        ]

        if telegram_id:
            client_request = await session.execute(
                select(Client).where(Client.telegram_id == telegram_id)
            )
            client = client_request.scalars().first()
            if not client:
                return False
            conditions.append(Appointment.client_id == client.id)

        appointment_request = await session.execute(
            select(Appointment).where(*conditions)
        )
        appointment = appointment_request.scalars().first()
        if not appointment:
            return False

        appointment.status = 'отменена'
        await session.commit()

        return True


async def get_appointments_for_period(start_date, end_date):
    """
    Возвращает все отсортированные по дате и времени записи за период,
    кроме отмененных.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Appointment).options(
                joinedload(Appointment.client),
                joinedload(Appointment.service)
            ).where(
                Appointment.date >= start_date,
                Appointment.date <= end_date,
                Appointment.status != 'отменена'
            ).order_by(Appointment.date, Appointment.start_time)
        )

        return result.unique().scalars().all()


async def update_appointment(appointment_id, new_date, new_start_time):
    """
    Переносит запись на новую дату и время, проверяя, что новый слот свободен.

    Возвращает объект Appointment или None, если запись не найдена,
    отменена или новый слот занят.
    """
    async with async_session() as session:
        appointment_request = await session.execute(
            select(Appointment).options(
                joinedload(Appointment.service)
            ).where(
                Appointment.id == appointment_id,
                Appointment.status != 'отменена'
            )
        )
        appointment = appointment_request.unique().scalars().first()
        if not appointment:
            return None

        new_start_dt = datetime.combine(new_date, new_start_time)
        new_end_dt = new_start_dt + timedelta(
            minutes=appointment.service.duration
        )
        new_end_time = new_end_dt.time()

        busy_request = await session.execute(
            select(Appointment).where(
                Appointment.date == new_date,
                Appointment.status != 'отменена',
                Appointment.id != appointment_id
            )
        )
        busy_appointments = busy_request.scalars().all()

        blocked_request = await session.execute(
            select(BlockedTime).where(BlockedTime.date == new_date)
        )
        blocked_times = blocked_request.scalars().all()

        if not _is_slot_free(
            new_start_time, new_end_time, busy_appointments, blocked_times
        ):
            return None

        day_of_week = new_date.weekday()
        wh_request = await session.execute(
            select(WorkingHours).where(
                WorkingHours.day_of_week == day_of_week,
                WorkingHours.is_working,
            )
        )
        working_hours = wh_request.scalars().first()
        if not working_hours:
            return None

        if (
            new_start_time < working_hours.start_time
            or new_end_time > working_hours.end_time
        ):
            return None

        appointment.date = new_date
        appointment.start_time = new_start_time
        appointment.end_time = new_end_time

        await session.commit()

        return appointment


async def create_blocked_time(day, start_time, end_time, reason=None):
    """
    Создает заблокированное время с проверкой, что новый блок не
    пересекается с записями и другими блокировками.

    Возвращает объект BlockedTime или None, если время занято.
    """
    async with async_session() as session:
        appointments_request = await session.execute(
            select(Appointment).where(
                Appointment.date == day,
                Appointment.status != 'отменена'
            )
        )
        appointments = appointments_request.scalars().all()

        blocked_request = await session.execute(
            select(BlockedTime).where(BlockedTime.date == day)
        )
        blocked_times = blocked_request.scalars().all()

        if not _is_slot_free(
            start_time, end_time, appointments, blocked_times
        ):
            return None

        blocked = BlockedTime(
            date=day,
            start_time=start_time,
            end_time=end_time,
            reason=reason
        )

        session.add(blocked)
        await session.commit()

        return blocked


async def get_blocked_times_for_period(start_date, end_date):
    """
    Возвращает отсортированное по дате и времени заблокированное
    время за период.
    """
    async with async_session() as session:
        result = await session.execute(
            select(BlockedTime)
            .where(
                BlockedTime.date >= start_date,
                BlockedTime.date <= end_date
            ).order_by(BlockedTime.date, BlockedTime.start_time)
        )

        return result.scalars().all()


async def delete_blocked_time(blocked_id):
    """Удаляет в календаре заблокированное время по ID."""
    async with async_session() as session:
        blocked = await session.get(BlockedTime, blocked_id)
        if not blocked:
            return False

        await session.delete(blocked)
        await session.commit()
        return True
