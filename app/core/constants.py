"""Константы проекта."""

from datetime import time
from zoneinfo import ZoneInfo

# Статусы записей
STATUS_PENDING = 'в ожидании'
STATUS_CANCELLED = 'отменена'

# Рабочее время по умолчанию
DEFAULT_WORK_START = time(10)
DEFAULT_WORK_END = time(20)

# Длины строк
MAX_LENGTH_NAME = 255
MAX_LENGTH_PHONE = 20
MAX_LENGTH_STATUS = 20

# Названия дней недели для отображения (0 = ПН, 6 = ВС)
DAYS_OF_WEEK_LABELS = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

# Дни недели
WORK_DAYS_COUNT = 5
WEEKEND_START_DAY = 5
WEEKEND_END_DAY = 7

# Услуги по умолчанию
DEFAULT_SERVICES = [
    {
        'name': 'Стрижка',
        'duration': 60,
        'price': 1500,
        'description': 'Женская стрижка любой сложности'
    },
    {
        'name': 'Окрашивание',
        'duration': 100,
        'price': 3500,
        'description': 'Окрашивание волос (краска включена в стоимость)'
    },
    {
        'name': 'Стрижка и окрашивание',
        'duration': 160,
        'price': 4500,
        'description': (
            'Комплекс: стрижка и окрашивание волос '
            '(краска включена в стоимость)'
        )
    }
]

# Клиенты
DEFAULT_CLIENT_NAME = 'Клиент'

# Бот и запись
DAYS_FOR_BOOKING = 14
SLOT_STEP_MINUTES = 30

# Напоминания клиентам
REMINDER_HOUR = 8
REMINDER_MINUTE = 0
REMINDER_RESET_HOUR = 0
REMINDER_RESET_MINUTE = 1
REMINDER_CHECK_INTERVAL_SECONDS = 60

# Календарь (API)
BLOCKED_ID_PREFIX = 'blocked_'
BLOCKED_TITLE = 'Занято'
BLOCKED_COLOR = 'gray'

# Экспорт CSV
CSV_DELIMITER = ';'
CSV_BOM = '\ufeff'
CSV_COLUMNS = ['Дата', 'Время', 'Клиент', 'Услуга', 'Цена', 'Статус']

# Авторизация
DEFAULT_CALENDAR_PASSWORD = 'admin'
AUTH_COOKIE_NAME = 'master_auth'

# Веб-приложение
APP_TITLE = 'Календарь записей'
HEALTH_OK = 'ok'

# Alembic
ASYNC_DRIVER_SUFFIX = '+asyncpg'
ENV_DATABASE_URL = 'DATABASE_URL'

# Публичные эндпоинты
PUBLIC_PATHS = ('/login', '/health')

# Часовой пояс для корректной работы дат
TIMEZONE = ZoneInfo('Europe/Moscow')
