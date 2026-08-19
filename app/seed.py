"""
Скрипт для первичного заполнения базы данных.

Создаёт услуги и настраивает рабочее время.

Запуск: python -m app.seed
"""

import asyncio

from app.core import constants
from app.database import async_session
from app.models import Service, WorkingHours


async def seed_services():
    """Добавляет базовые услуги в БД."""
    services = [
        Service(**service_data)
        for service_data in constants.DEFAULT_SERVICES
    ]

    async with async_session() as session:
        for service in services:
            session.add(service)
        await session.commit()

    print('Услуги добавлены.')


async def seed_working_hours():
    """Настраивает в БД рабочее время: ПН-ПТ 10:00-20:00, СБ-ВС - выходные."""
    working_hours = []

    for day in range(constants.WORK_DAYS_COUNT):
        working_hours.append(
            WorkingHours(
                day_of_week=day,
                start_time=constants.DEFAULT_WORK_START,
                end_time=constants.DEFAULT_WORK_END,
                is_working=True
            )
        )

    for day in range(constants.WEEKEND_START_DAY, constants.WEEKEND_END_DAY):
        working_hours.append(
            WorkingHours(
                day_of_week=day,
                is_working=False
            )
        )

    async with async_session() as session:
        for wh in working_hours:
            session.add(wh)
        await session.commit()

    print('Рабочее время настроено.')


async def main():
    """Запускает первичное заполнение БД."""
    await seed_services()
    await seed_working_hours()

    print('База данных заполнена.')


if __name__ == '__main__':
    asyncio.run(main())
