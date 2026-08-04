"""
Бизнес-логика для работы с записями, услугами и расписанием.

Предоставляет функции для бота и веб-календаря.
"""

from datetime import datetime, timedelta

from sqlalchemy import select

from app.database import async_session
from app.models import Service, Appointment, WorkingHours, BlockedTime


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
    Возвращает список свободного времени для записи на указанную дату и услугу.
    """
    async with async_session() as session:
        service_result = await session.execute(
            select(Service).where(Service.id == service_id)
        )
        service = service_result.scalars().first()
        if not service:
            return []

        duration = service.duration

        day_of_week = day.weekday()
        wh_result = await session.execute(
            select(WorkingHours).where(
                WorkingHours.day_of_week == day_of_week,
                WorkingHours.is_working
            )
        )
        working_hours = wh_result.scalars().first()
        if not working_hours:
            return []

        appointments_result = await session.execute(
            select(Appointment).where(
                Appointment.date == day,
                Appointment.status != 'отменена'
            )
        )
        appointments = appointments_result.scalars().all()

        blocked_result = await session.execute(
            select(BlockedTime).where(BlockedTime.date == day)
        )
        blocked_times = blocked_result.scalars().all()

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
