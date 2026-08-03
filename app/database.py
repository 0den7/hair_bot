"""
Модуль для подключения к базе данных PostgreSQL.

Предоставляет асинхронный движок, фабрику сессий и базовый класс
для ORM-моделей.
"""

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError(
        'Переменная DATABASE_URL не найдена. '
        'Проверьте, что файл .env существует и содержит DATABASE_URL'
    )

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""


async def get_db():
    """
    Генератор асинхронных сессий с автоматическим коммитом, откатом и
    закрытием сессии.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
