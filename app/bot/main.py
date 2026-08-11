"""
Точка входа Telegram бота.

Создаёт бота, диспетчер, подключает роутеры и запускает polling.
"""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.config import BOT_TOKEN
from app.bot.handlers import start, booking, appointments


async def main():
    """Запуск бота."""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(booking.router)
    dp.include_router(appointments.router)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
