"""
Фоновая задача для отправки напоминаний клиентам в 8:00 в день записи.
"""

import asyncio
from datetime import datetime, time

from aiogram import Bot

from app.bot.config import BOT_TOKEN
from app.core import constants
from app.services.booking import get_appointments_for_today


async def send_reminders():
    """Отправляет напоминания о сегодняшних записях в 8:00."""
    bot = Bot(token=BOT_TOKEN)
    sent_today = False

    while True:
        now = datetime.now()
        current_time = now.time()

        if current_time < time(
            constants.REMINDER_RESET_HOUR,
            constants.REMINDER_RESET_MINUTE
        ):
            sent_today = False

        if current_time >= time(
            constants.REMINDER_HOUR,
            constants.REMINDER_MINUTE
        ) and not sent_today:
            appointments = await get_appointments_for_today()

            for app in appointments:
                if app.client.telegram_id:
                    try:
                        await bot.send_message(
                            chat_id=app.client.telegram_id,
                            text=(
                                f'Напоминание!\n\n'
                                f'Сегодня в '
                                f'{app.start_time.strftime("%H:%M")} '
                                f'у вас запись: {app.service.name}.\n\n'
                                f'Ждём вас!'
                            )
                        )
                    except Exception:
                        pass

            sent_today = True

        await asyncio.sleep(constants.REMINDER_CHECK_INTERVAL_SECONDS)
