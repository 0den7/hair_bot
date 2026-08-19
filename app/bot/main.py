"""
Точка входа Telegram бота.

Создаёт бота, диспетчер, подключает роутеры и запускает polling.
"""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramAPIError

from app.bot.config import BOT_TOKEN
from app.bot.handlers import start, booking, appointments
from app.bot.reminders import send_reminders


async def main():
    """Запуск бота."""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(booking.router)
    dp.include_router(appointments.router)

    @dp.error()
    async def error_handler(event, exception):
        """Логирует неожиданные ошибки."""
        if isinstance(exception, TelegramAPIError):
            print(
                f'Ошибка Telegram API '
                f'{type(event).__name__}: {exception}'
            )
        else:
            print(
                f'Неожиданная ошибка '
                f'{type(event).__name__}: {exception}'
            )

    asyncio.create_task(send_reminders())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
