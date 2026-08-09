"""
Обработчики: /start и кнопка 'Назад (в главное меню)'.
"""

from aiogram import Router, F
from aiogram.filters import Command
from sqlalchemy import select

from app.bot.keyboards.keyboard import get_main_menu
from app.database import async_session
from app.models import Client

router = Router()


@router.message(Command('start'))
async def cmd_start(message):
    """
    Обработчик команды /start.

    Создаёт или обновляет клиента в БД, показывает приветствие и главное меню.
    """
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name or 'Клиент'
    last_name = message.from_user.last_name

    async with async_session() as session:
        result = await session.execute(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        client = result.scalars().first()

        if client:
            client.username = username
            client.first_name = first_name
            client.last_name = last_name
        else:
            client = Client(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(client)

        await session.commit()

    await message.answer(
        f'Здравствуйте, {first_name}!\n\n'
        f'Я бот для записи на стрижку и окрашивание к Наталье.\n'
        f'Выберите действие:',
        reply_markup=get_main_menu()
    )


@router.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback, state):
    """
    Обработчик кнопки 'Назад (в главное меню)'.

    Сбрасывает состояние FSM и возвращает пользователя в главное меню.
    """
    await state.clear()
    await callback.message.edit_text(
        'Выберите действие:',
        reply_markup=get_main_menu()
    )
    await callback.answer()
