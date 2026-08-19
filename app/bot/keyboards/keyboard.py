"""
Клавиатуры для Telegram бота.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_back_button():
    """Клавиатура с кнопкой возврата в главное меню."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='◀️ Назад',
                    callback_data='back_to_menu'
                )
            ]
        ]
    )


def get_main_menu():
    """Главное меню бота."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='📅 Записаться',
                    callback_data='book'
                )
            ],
            [
                InlineKeyboardButton(
                    text='📋 Мои записи',
                    callback_data='my_appointments'
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Отменить запись',
                    callback_data='cancel_menu'
                )
            ]
        ]
    )


def get_confirm_keyboard():
    """Клавиатура подтверждения/отмены."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='✅ Подтвердить',
                    callback_data='confirm'
                ),
                InlineKeyboardButton(
                    text='❌ Отмена',
                    callback_data='cancel_booking'
                )
            ]
        ]
    )


def get_services_keyboard(services):
    """Клавиатура выбора услуги."""
    buttons = []
    for service in services:
        buttons.append([
            InlineKeyboardButton(
                text=f'{service.name} ({service.duration} мин, '
                     f'{service.price}₽)',
                callback_data=f'select_service:{service.id}'
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text='◀️ Назад',
            callback_data='back_to_menu'
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_dates_keyboard(dates):
    """Клавиатура выбора даты."""
    buttons = []
    for date_item in dates:
        buttons.append([
            InlineKeyboardButton(
                text=date_item['label'],
                callback_data=f'select_date:{date_item['value']}'
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text='◀️ Назад',
            callback_data='back_to_services'
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_slots_keyboard(slots):
    """Клавиатура выбора времени."""
    buttons = []
    for slot in slots:
        time_str = slot.strftime('%H:%M')
        buttons.append([
            InlineKeyboardButton(
                text=time_str,
                callback_data=f'select_slot:{time_str}'
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text='◀️ Назад',
            callback_data='back_to_dates'
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_appointments_keyboard(appointments):
    """Клавиатура со списком записей клиента для отмены."""
    buttons = []
    for app in appointments:
        date_str = app.date.strftime('%d.%m.%Y')
        time_str = app.start_time.strftime('%H:%M')
        buttons.append([
            InlineKeyboardButton(
                text=f'{date_str} в {time_str} — {app.service.name}',
                callback_data=f'appointment:{app.id}'
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text='◀️ Назад',
            callback_data='back_to_menu'
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_after_cancel_keyboard():
    """Клавиатура после отмены записи."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='📅 Записаться заново',
                    callback_data='book'
                )
            ],
            [
                InlineKeyboardButton(
                    text='В меню',
                    callback_data='back_to_menu'
                )
            ]
        ]
    )
