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
    """Возвращает список записей за период."""
    appointments = await get_appointments_for_period(start, end)

    return [
        {
            'id': app.id,
            'date': app.date.isoformat(),
            'start_time': app.start_time.strftime('%H:%M'),
            'end_time': app.end_time.strftime('%H:%M'),
            'status': app.status,
            'client_name': app.client.first_name,
            'service_name': app.service.name,
            'service_duration': app.service.duration
        }
        for app in appointments
    ]
