"""
Обработчики процесса записи (FSM).

Шаги: выбор услуги -> выбор даты -> выбор времени -> подтверждение.
"""

from datetime import date, time

from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup

from app.bot.keyboards.keyboard import (
    get_services_keyboard,
    get_back_button,
    get_dates_keyboard,
    get_slots_keyboard,
    get_confirm_keyboard,
    get_main_menu
)
from app.services.booking import (
    get_active_services,
    get_available_dates,
    get_available_slots,
    get_service_by_id,
    create_appointment
)

router = Router()


class BookingStates(StatesGroup):
    """Состояния процесса записи."""
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()
    confirming = State()


@router.callback_query(F.data == 'book')
async def start_booking(callback, state):
    """
    Начало процесса записи.

    Переводит клиента в состояние выбора услуги, загружает услуги из БД и
    показывает клавиатуру.
    """
    services = await get_active_services()

    if not services:
        await callback.message.edit_text(
            'Нет доступных услуг',
            reply_markup=get_back_button()
        )
        await callback.answer('Вы вернулись в главное меню')
        return

    await state.set_state(BookingStates.choosing_service)

    await callback.message.edit_text(
        'Выберите услугу:',
        reply_markup=get_services_keyboard(services)
    )
    await callback.answer()


@router.callback_query(
    BookingStates.choosing_service,
    F.data.startswith('select_service:')
)
async def service_process(callback, state):
    """
    Обработчик выбора услуги.

    Сохраняет service_id и показывает клавиатуру для выбора даты записи.
    """
    service_id = int(callback.data.split(':')[1])
    await state.update_data(service_id=service_id)

    dates = await get_available_dates()

    if not dates:
        await callback.message.edit_text(
            'Нет доступных дат. Выберите другую услугу:',
            reply_markup=get_services_keyboard(await get_active_services())
        )
        await callback.answer()
        return

    await state.set_state(BookingStates.choosing_date)

    await callback.message.edit_text(
        'Выберите дату:',
        reply_markup=get_dates_keyboard(dates)
    )
    await callback.answer()


@router.callback_query(
    BookingStates.choosing_date,
    F.data.startswith('select_date:')
)
async def date_process(callback, state):
    """
    Обработчик выбора даты.

    Сохраняет дату и показывает клавиатуру для выбора времени записи.
    """
    date_str = callback.data.split(':')[1]
    selected_date = date.fromisoformat(date_str)

    await state.update_data(date=date_str)

    service_id = (await state.get_data())['service_id']

    slots = await get_available_slots(selected_date, service_id)

    if not slots:
        await callback.message.edit_text(
            'Нет доступного времени на эту дату. Выберите другую дату:',
            reply_markup=get_dates_keyboard(await get_available_dates())
        )
        await callback.answer()
        return

    await state.set_state(BookingStates.choosing_time)

    await callback.message.edit_text(
        'Выберите время:',
        reply_markup=get_slots_keyboard(slots)
    )
    await callback.answer()


@router.callback_query(
    BookingStates.choosing_time,
    F.data.startswith('select_slot:')
)
async def time_process(callback, state):
    """
    Обработчик выбора времени.

    Сохраняет время и показывает подтверждение с деталями записи.
    """
    time_str = callback.data.split(':')[1]
    await state.update_data(time=time_str)

    data = await state.get_data()
    selected_service_id = data['service_id']
    selected_date = date.fromisoformat(data['date'])

    service = await get_service_by_id(selected_service_id)

    date_label = selected_date.strftime('%d.%m.%Y')

    text = (
        f'Проверьте детали записи:\n\n'
        f'Услуга: {service.name}\n'
        f'Дата: {date_label}\n'
        f'Время: {time_str}\n\n'
        f'Всё верно?'
    )

    await state.set_state(BookingStates.confirming)

    await callback.message.edit_text(
        text,
        reply_markup=get_confirm_keyboard()
    )
    await callback.answer()


@router.callback_query(
    BookingStates.confirming,
    F.data == 'confirm'
)
async def confirm_process(callback, state):
    """
    Обработчик подтверждения записи.

    Создаёт запись в БД. Если слот занят - предлагает выбрать другое время.
    """
    data = await state.get_data()
    telegram_id = callback.from_user.id
    service_id = data['service_id']
    selected_date = date.fromisoformat(data['date'])
    time_parts = data['time'].split(':')
    start_time = time(int(time_parts[0]), int(time_parts[1]))

    appointment = await create_appointment(
        telegram_id=telegram_id,
        service_id=service_id,
        day=selected_date,
        start_time=start_time
    )

    if appointment:
        await state.clear()
        date_label = selected_date.strftime('%d.%m.%Y')
        await callback.message.edit_text(
            f'Вы записаны!\n\n'
            f'Дата: {date_label}\n'
            f'Время: {data['time']}\n\n'
            f'Ждём вас!'
        )
    else:
        slots = await get_available_slots(selected_date, service_id)
        if slots:
            await state.set_state(BookingStates.choosing_time)
            await callback.message.edit_text(
                'Это время только что заняли. Выберите другое:',
                reply_markup=get_slots_keyboard(slots)
            )
        else:
            await state.clear()
            await callback.message.edit_text(
                'К сожалению, свободного времени не осталось.',
                reply_markup=get_main_menu()
            )

    await callback.answer()


@router.callback_query(
    BookingStates.confirming,
    F.data == 'cancel_booking'
)
async def cancel_booking_process(callback, state):
    """
    Обработчик кнопки 'Отмена' на шаге подтверждения.

    Сбрасывает процесс записи и возвращает в главное меню.
    """
    await state.clear()
    await callback.message.edit_text(
        'Запись отменена. Выберите действие:',
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == 'back_to_services')
async def back_to_services(callback, state):
    """
    Обработчик кнопки 'Назад' на шаге выбора даты.

    Возвращает клиента к выбору услуги.
    """
    services = await get_active_services()

    if not services:
        await state.clear()
        await callback.message.edit_text(
            'Нет доступных услуг.',
            reply_markup=get_back_button()
        )
        await callback.answer()
        return

    await state.set_state(BookingStates.choosing_service)

    await callback.message.edit_text(
        'Выберите услугу:',
        reply_markup=get_services_keyboard(services)
    )
    await callback.answer()


@router.callback_query(F.data == 'back_to_dates')
async def back_to_dates(callback, state):
    """
    Обработчик кнопки 'Назад' на шаге выбора времени.

    Возвращает клиента к выбору даты.
    """
    dates = await get_available_dates()

    if not dates:
        await state.set_state(BookingStates.choosing_service)
        await callback.message.edit_text(
            'Нет доступных дат. Выберите другую услугу:',
            reply_markup=get_services_keyboard(await get_active_services())
        )
        await callback.answer()
        return

    await state.set_state(BookingStates.choosing_date)

    await callback.message.edit_text(
        'Выберите дату:',
        reply_markup=get_dates_keyboard(dates)
    )
    await callback.answer()
