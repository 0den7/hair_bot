"""
Конфигурация Telegram бота.

Загружает токен из переменных окружения.
"""

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError(
        'Переменная BOT_TOKEN не найдена. '
        'Проверьте, что файл .env существует и содержит BOT_TOKEN.'
    )
