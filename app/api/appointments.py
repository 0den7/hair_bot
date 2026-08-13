"""
API для работы с записями.

Эндпоинты для получения списка записей за период.
"""

from datetime import date, time

from fastapi import APIRouter, Query, Body

from app.services.booking import (
    get_appointments_for_period,
    update_appointment,
    cancel_appointment
)

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


@router.put('/{appointment_id}/move')
async def move_appointment(
    appointment_id: int,
    new_date: date = Body(..., embed=True),
    new_time: str = Body(..., embed=True)
):
    """Переносит запись на новую дату и время."""
    hour, minute = map(int, new_time.split(':'))
    new_start_time = time(hour, minute)

    appointment = await update_appointment(
        appointment_id=appointment_id,
        new_date=new_date,
        new_start_time=new_start_time
    )

    if not appointment:
        return {
            'success': False,
            'message': 'Слот занят или запись не найдена'
        }

    return {'success': True}


@router.delete('/{appointment_id}')
async def cancel_appointment_by_master(appointment_id: int):
    """Отмена записи мастером."""
    success = await cancel_appointment(appointment_id)

    if not success:
        return {
            'success': False,
            'message': 'Запись не найдена или уже отменена'
        }

    return {'success': True}
