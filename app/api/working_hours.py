"""
API для управления рабочим временем.
"""

from datetime import time

from fastapi import APIRouter, Body

from app.services.booking import (
    get_working_hours,
    update_working_hours
)

router = APIRouter(prefix='/api/working-hours', tags=['working-hours'])


@router.get('/')
async def get_hours():
    """Возвращает настройки рабочего времени на все дни недели."""
    working_hours = await get_working_hours()
    days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

    return [
        {
            'day_of_week': wh.day_of_week,
            'label': days[wh.day_of_week],
            'start_time': wh.start_time.strftime('%H:%M'),
            'end_time': wh.end_time.strftime('%H:%M'),
            'is_working': wh.is_working
        }
        for wh in working_hours
    ]


@router.put('/{day_of_week}')
async def edit_hours(
    day_of_week: int,
    start_time: str = Body(None),
    end_time: str = Body(None),
    is_working: bool = Body(None)
):
    """Обновляет настройки дня недели."""
    start_time_obj = None
    end_time_obj = None

    if start_time:
        h, m = map(int, start_time.split(':'))
        start_time_obj = time(h, m)

    if end_time:
        h, m = map(int, end_time.split(':'))
        end_time_obj = time(h, m)

    updated = await update_working_hours(
        day_of_week=day_of_week,
        start_time=start_time_obj,
        end_time=end_time_obj,
        is_working=is_working
    )

    if not updated:
        return {'success': False, 'message': 'День не найден'}

    return {'success': True}
