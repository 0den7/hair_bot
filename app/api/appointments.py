"""
API для работы с записями.
"""

import csv
from datetime import date, time
from io import StringIO

from fastapi import APIRouter, Query, Body
from fastapi.responses import StreamingResponse

from app.services.booking import (
    get_appointments_for_period,
    update_appointment,
    cancel_appointment,
    create_blocked_time,
    get_blocked_times_for_period,
    delete_blocked_time,
    create_appointment_by_master
)

router = APIRouter(prefix='/api/appointments', tags=['appointments'])


@router.get('/')
async def get_appointments(
    start: date = Query(..., description='Начало периода (YYYY-MM-DD)'),
    end: date = Query(..., description='Конец периода (YYYY-MM-DD)')
):
    """Возвращает список записей за период в формате FullCalendar."""
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
    """Перенос мастером записи на новую дату и время."""
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


@router.post('/blocked')
async def block_time(
    day: date = Body(...),
    start_time: str = Body(...),
    end_time: str = Body(...),
    reason: str = Body(None)
):
    """Блокировка времени мастером."""
    start_h, start_m = map(int, start_time.split(':'))
    end_h, end_m = map(int, end_time.split(':'))

    blocked = await create_blocked_time(
        day=day,
        start_time=time(start_h, start_m),
        end_time=time(end_h, end_m),
        reason=reason
    )

    if not blocked:
        return {'success': False, 'message': 'Время уже занято'}

    return {'success': True, 'id': blocked.id}


@router.get('/blocked')
async def get_blocked_times(
    start: date = Query(..., description='Начало периода'),
    end: date = Query(..., description='Конец периода')
):
    """Возвращает заблокированное время за период в формате FullCalendar."""
    blocked_times = await get_blocked_times_for_period(start, end)

    return [
        {
            'id': f'blocked_{bt.id}',
            'title': 'Занято',
            'start': (
                f'{bt.date.isoformat()}'
                f'T{bt.start_time.strftime("%H:%M")}'
            ),
            'end': (
                f'{bt.date.isoformat()}'
                f'T{bt.end_time.strftime("%H:%M")}'
            ),
            'color': 'gray'
        }
        for bt in blocked_times
    ]


@router.delete('/blocked/{blocked_id}')
async def delete_blocked(blocked_id: int):
    """Удаление блокировки мастером."""
    success = await delete_blocked_time(blocked_id)

    if not success:
        return {'success': False, 'message': 'Блокировка не найдена'}

    return {'success': True}


@router.post('/create')
async def create_appointment(
    client_name: str = Body(...),
    service_id: int = Body(...),
    day: date = Body(...),
    start_time: str = Body(...)
):
    """Создание записи мастером."""
    start_h, start_m = map(int, start_time.split(':'))
    appointment = await create_appointment_by_master(
        client_name=client_name,
        service_id=service_id,
        day=day,
        start_time=time(start_h, start_m)
    )

    if not appointment:
        return {
            'success': False,
            'message': 'Услуга не найдена или слот занят'
        }

    return {'success': True, 'id': appointment.id}


@router.get('/export')
async def export_appointments(
    start: date = Query(...),
    end: date = Query(...)
):
    """Возвращает CSV-файл с записями за период."""
    appointments = await get_appointments_for_period(start, end)

    output = StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Дата', 'Время', 'Клиент', 'Услуга', 'Цена', 'Статус'])

    for app in appointments:
        writer.writerow([
            app.date.strftime('%d.%m.%Y'),
            app.start_time.strftime('%H:%M'),
            app.client.first_name,
            app.service.name,
            app.service.price,
            app.status
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=appointments.csv'
        }
    )
