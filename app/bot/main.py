"""
Точка входа Telegram бота.

Создает бота, диспетчер, подключает роутеры, запускает polling,
логирует ошибки и уведомляет админа.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.config import ADMIN_TELEGRAM_ID, BOT_TOKEN
from app.bot.handlers import appointments, booking, start
from app.bot.reminders import send_reminders

logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Запуск бота."""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(booking.router)
    dp.include_router(appointments.router)

    @dp.error()
    async def error_handler(event, exception):
        """Логирует ошибки и уведомляет админа."""
        if isinstance(exception, TelegramAPIError):
            message = (
                f'Ошибка Telegram API '
                f'{type(event).__name__}: {exception}'
            )
        else:
            message = (
                f'Неожиданная ошибка '
                f'{type(event).__name__}: {exception}'
            )

        logger.error(message)

        try:
            await bot.send_message(
                chat_id=ADMIN_TELEGRAM_ID,
                text=message
            )
        except Exception:
            logger.exception('Не удалось отправить уведомление админу')

    asyncio.create_task(send_reminders())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
