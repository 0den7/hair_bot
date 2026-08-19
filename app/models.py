"""
Модели SQLAlchemy.

Описывает таблицы: клиенты, услуги, записи, рабочее время, заблокированное
время.
"""

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import relationship

from app.core import constants
from app.database import Base


class Client(Base):
    """
    Клиент.

    Создаётся автоматически при первом обращении к боту (/start).
    """

    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    username = Column(String(constants.MAX_LENGTH_NAME), nullable=True)
    first_name = Column(String(constants.MAX_LENGTH_NAME), nullable=False)
    last_name = Column(String(constants.MAX_LENGTH_NAME), nullable=True)
    phone = Column(String(constants.MAX_LENGTH_PHONE), nullable=True)

    appointments = relationship('Appointment', back_populates='client')

    def __repr__(self):
        if self.username:
            return f'<Клиент {self.first_name} (@{self.username})>'
        return f'<Клиент {self.first_name}>'


class Service(Base):
    """
    Услуга.

    Настраивается через веб-интерфейс.
    """

    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String(constants.MAX_LENGTH_NAME),
        unique=True,
        nullable=False
    )
    duration = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    appointments = relationship('Appointment', back_populates='service')

    def __repr__(self):
        return f'<Услуга {self.name} ({self.duration} мин, {self.price}₽)>'


class Appointment(Base):
    """
    Запись клиента на услугу.
    """

    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(
        String(constants.MAX_LENGTH_STATUS),
        nullable=False,
        default=constants.STATUS_PENDING
    )
    notes = Column(Text, nullable=True)

    client = relationship('Client', back_populates='appointments')
    service = relationship('Service', back_populates='appointments')

    def __repr__(self):
        return (
            f'<Запись {self.date} {self.start_time} '
            f'- {self.client.first_name}>'
        )


class WorkingHours(Base):
    """
    Рабочее время мастера.

    Настраивается через веб-интерфейс.
    """

    __tablename__ = 'working_hours'

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, unique=True, nullable=False)
    start_time = Column(
        Time,
        nullable=False,
        default=constants.DEFAULT_WORK_START
    )
    end_time = Column(Time, nullable=False, default=constants.DEFAULT_WORK_END)
    is_working = Column(Boolean, default=True)

    def __repr__(self):
        return (
            f'<Рабочее время '
            f'{constants.DAYS_OF_WEEK_LABELS[self.day_of_week]} '
            f'{self.start_time}-{self.end_time}>'
        )


class BlockedTime(Base):
    """
    Заблокированное время (личные дела мастера).

    Настраивается через веб-интерфейс.
    """

    __tablename__ = 'blocked_time'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    reason = Column(String(constants.MAX_LENGTH_NAME), nullable=True)

    def __repr__(self):
        return (
            f'<Нерабочее время {self.date} '
            f'{self.start_time}-{self.end_time}>'
        )
