# HairBot — сервис записи к мастеру

Сервис онлайн-записи для частных мастеров. Клиенты записываются через Telegram-бота, а мастер управляет расписанием, услугами и графиком через веб-календарь.

## Возможности

**Для клиента (Telegram-бот):**

- Пошаговая запись: выбор услуги → даты → времени → подтверждение

- Просмотр своих активных записей

- Отмена записи с предложением записаться заново

- Утренние напоминания в день записи

**Для мастера (веб-календарь):**

- Просмотр записей за неделю и месяц

- Создание записи вручную

- Перенос записи drag-and-drop

- Отмена записи

- Блокировка времени под личные дела

- Отмена блокировки времени

- Управление услугами: создание, редактирование, скрытие, удаление

- Управление рабочим временем по дням недели

- Экспорт записей в CSV

- Защита API и календаря паролем

## Стек технологий

- Python 3.12+

- Aiogram 3.30+

- FastAPI 0.141+

- SQLAlchemy 2.0+

- Uvicorn

- Alembic

- PostgreSQL

- FullCalendar.js

- HTML

- CSS

- JavaScript ES6+

- Jinja2

- Git и GitHub

## Архитектура

Проект разделён на два интерфейса и общий слой бизнес-логики:

- **Telegram-бот** (Aiogram) — интерфейс для клиентов
- **Веб-календарь** (FastAPI + FullCalendar) — интерфейс для мастера
- **Слой бизнес-логики** (на SQLAlchemy) — общая логика, работает с PostgreSQL

Оба интерфейса используют одну базу данных и одни и те же функции бизнес-логики.

## Как запустить локально

### 1. Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone git@github.com:0den7/hair_bot.git
```

```bash
cd hair_bot
```

### 2. Создать и активировать виртуальное окружение:

```bash
python -m venv venv
```

Windows:

```bash
source venv/Scripts/activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Установить зависимости:

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### 4. Получить токен Telegram-бота:

1. Найти в Telegram бота `@BotFather`
2. Отправить `/newbot`
3. Указать имя и username бота
4. Сохранить полученный токен (он понадобится для `.env`)

### 5. Настроить переменные окружения:

Создать файл `.env` в корне проекта (см. `.env.example`):

```env
DB_NAME=hairsalon
DB_USER=postgres
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hairsalon
BOT_TOKEN=your_telegram_bot_token
CALENDAR_PASSWORD=your_calendar_password
```

### 6. Создать базу данных PostgreSQL:

```bash
psql -U postgres -c "CREATE DATABASE hairsalon;"
```

### 7. Применить миграции:

```bash
alembic upgrade head
```

### 8. Заполнить базу начальными данными:

```bash
python -m app.seed
```

### 9. Запустить Telegram-бота:

```bash
python -m app.bot.main
```

### 10. Запустить веб-календарь (в отдельном терминале):

```bash
uvicorn app.api.main:app --reload --port 8000
```

Проект будет доступен по адресу `http://127.0.0.1:8000/`

## Резервное копирование базы данных

Создание дампа:

```bash
python backup.py
```

Файл появится в папке `backups/`.

Восстановление:

```bash
psql -U postgres -d hairsalon -f backups/backup_YYYY-MM-DD_HH-MM-SS.sql
```

## Документация API

Документация доступна после входа в календарь по адресу:

```text
http://127.0.0.1:8000/docs
```

## Эндпоинты API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Веб-календарь мастера |
| GET | `/api/appointments/` | Список записей за период |
| POST | `/api/appointments/create` | Создание записи мастером |
| PUT | `/api/appointments/{appointment_id}/move` | Перенос записи мастером |
| DELETE | `/api/appointments/{appointment_id}` | Отмена записи мастером |
| POST | `/api/appointments/blocked` | Блокировка времени мастером |
| GET | `/api/appointments/blocked` | Список блокировок за период |
| DELETE | `/api/appointments/blocked/{blocked_id}` | Удаление блокировки мастером |
| GET | `/api/appointments/export` | Экспорт записей в CSV |
| GET | `/api/services/` | Список всех услуг |
| POST | `/api/services/` | Создание услуги |
| PUT | `/api/services/{service_id}` | Обновление услуги |
| POST | `/api/services/{service_id}/toggle` | Переключение активности услуги |
| DELETE | `/api/services/{service_id}` | Удаление услуги |
| GET | `/api/working-hours/` | Рабочее время |
| PUT | `/api/working-hours/{day_of_week}` | Обновление рабочего времени дня |
| GET | `/login` | Страница входа |
| POST | `/login` | Обработка входа |
| GET | `/logout` | Выход |
| GET | `/health` | Проверка работоспособности |

## Права доступа

- **Клиент** — через Telegram-бота: пошаговая запись, просмотр и отмена своих записей, получение напоминаний о записях
- **Мастер** — через веб-календарь с паролем: создание, перенос и отмена записей, блокировка времени, управление услугами и рабочим временем, экспорт записей в CSV

## Автор

**Юрий Кудряшов**

GitHub: [0den7](https://github.com/0den7)
