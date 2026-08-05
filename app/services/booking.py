"""
Бизнес-логика для работы с записями, услугами и расписанием.

Предоставляет функции для бота и веб-календаря.
"""

from datetime import datetime, timedelta

from sqlalchemy import select

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
            select(Appointment).where(
                Appointment.client_id == client.id,
                Appointment.status != 'отменена'
            ).order_by(Appointment.date, Appointment.start_time)
        )

        return result.scalars().all()


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
    кроме отменённых.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Appointment)
            .where(
                Appointment.date >= start_date,
                Appointment.date <= end_date,
                Appointment.status != 'отменена'
            ).order_by(Appointment.date, Appointment.start_time)
        )

        return result.scalars().all()


async def update_appointment(appointment_id, new_date, new_start_time):
    """
    Переносит запись на новую дату и время, проверяя, что новый слот свободен.

    Возвращает объект Appointment или None, если запись не найдена,
    отменена или новый слот занят.
    """
    async with async_session() as session:
        appointment_request = await session.execute(
            select(Appointment).where(
                Appointment.id == appointment_id,
                Appointment.status != 'отменена'
            )
        )
        appointment = appointment_request.scalars().first()
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

        appointment.date = new_date
        appointment.start_time = new_start_time
        appointment.end_time = new_end_time

        await session.commit()

        return appointment
