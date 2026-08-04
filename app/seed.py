"""
Скрипт для первичного заполнения базы данных.

Создаёт услуги и настраивает рабочее время.

Запуск: python -m app.seed
"""

import asyncio
from datetime import time

from app.database import async_session
from app.models import Service, WorkingHours


async def seed_services():
    """Добавляет базовые услуги в БД."""
    services = [
        Service(
            name='Стрижка',
            duration=60,
            price=1500,
            description='Женская стрижка любой сложности'
        ),
        Service(
            name='Окрашивание',
            duration=100,
            price=3500,
            description='Окрашивание волос (краска включена в стоимость)'
        ),
        Service(
            name='Стрижка и окрашивание',
            duration=160,
            price=4500,
            description=(
                'Комплекс: стрижка и окрашивание волос '
                '(краска включена в стоимость)'
            )
        )
    ]

    async with async_session() as session:
        for service in services:
            session.add(service)
        await session.commit()

    print('Услуги добавлены.')


async def seed_working_hours():
    """Настраивает в БД рабочее время: ПН-ПТ 10:00-20:00, СБ-ВС - выходные."""
    working_hours = []

    for day in range(5):
        working_hours.append(
            WorkingHours(
                day_of_week=day,
                start_time=time(10),
                end_time=time(20),
                is_working=True
            )
        )

    for day in range(5, 7):
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
