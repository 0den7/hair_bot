"""
Обработчики: 'Мои записи' и 'Отмена записи'.
"""

from aiogram import Router, F

from app.bot.keyboards.keyboard import (
    get_appointments_keyboard,
    get_back_button,
    get_main_menu,
    get_after_cancel_keyboard
)
from app.services.booking import (
    cancel_appointment,
    get_client_appointments
)

router = Router()


async def _get_appointments_or_show_empty(callback, empty_message):
    """
    Загружает записи клиента. Если записей нет - показывает сообщение
    с кнопкой 'Назад' и возвращает None.
    """
    appointments = await get_client_appointments(callback.from_user.id)

    if not appointments:
        await callback.message.edit_text(
            empty_message,
            reply_markup=get_back_button(),
        )
        await callback.answer()
        return

    return appointments


@router.callback_query(F.data == 'my_appointments')
async def my_appointments(callback):
    """
    Обработчик кнопки 'Мои записи'.

    Показывает список активных записей клиента.
    """
    appointments = await _get_appointments_or_show_empty(
        callback, 'У вас нет активных записей.'
    )
    if not appointments:
        return

    lines = ['Ваши записи:\n']
    for app in appointments:
        date_str = app.date.strftime('%d.%m.%Y')
        time_str = app.start_time.strftime('%H:%M')
        lines.append(f'{date_str} в {time_str} — {app.service.name}')

    await callback.message.edit_text(
        '\n'.join(lines),
        reply_markup=get_back_button(),
    )
    await callback.answer()


@router.callback_query(F.data == 'cancel_menu')
async def cancel_menu(callback):
    """
    Обработчик кнопки 'Отменить запись'.

    Показывает список записей для выбора отменяемой.
    """
    appointments = await _get_appointments_or_show_empty(
        callback, 'У вас нет активных записей для отмены.'
    )
    if not appointments:
        return

    await callback.message.edit_text(
        'Выберите запись для отмены:',
        reply_markup=get_appointments_keyboard(appointments)
    )
    await callback.answer()


@router.callback_query(F.data.startswith('appointment:'))
async def cancel_appointment_handler(callback):
    """
    Обработчик выбора конкретной записи для отмены.

    Отменяет запись и показывает результат.
    """
    success = await cancel_appointment(
        int(callback.data.split(':')[1]),
        callback.from_user.id
    )

    if success:
        if success:
            await callback.message.edit_text(
                'Запись отменена. Хотите записаться заново?',
                reply_markup=get_after_cancel_keyboard()
            )
    else:
        await callback.message.edit_text(
            'Не удалось отменить запись. Возможно, она уже отменена.',
            reply_markup=get_main_menu()
        )
    await callback.answer()
