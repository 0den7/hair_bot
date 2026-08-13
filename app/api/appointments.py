"""
API для работы с записями.

Эндпоинты для получения списка записей за период.
"""

from datetime import date

from fastapi import APIRouter, Query

from app.services.booking import get_appointments_for_period

router = APIRouter(prefix='/api/appointments', tags=['appointments'])


@router.get('/')
async def get_appointments(
    start: date = Query(..., description='Начало периода (YYYY-MM-DD)'),
    end: date = Query(..., description='Конец периода (YYYY-MM-DD)')
):
    """Возвращает список записей в формате FullCalendar."""
    appointments = await get_appointments_for_period(start, end)

    return [
        {
            'id': app.id,
            'title': f'{app.client.first_name} — {app.service.name}',
            'start': (
                f'{app.date.isoformat()}'
                f'T{app.start_time.strftime("%H:%M")}'
            ),
            'end': (
                f'{app.date.isoformat()}'
                f'T{app.end_time.strftime("%H:%M")}'
            ),
            'status': app.status
        }
        for app in appointments
    ]
