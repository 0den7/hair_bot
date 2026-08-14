"""
Модели SQLAlchemy.

Описывает таблицы: клиенты, услуги, записи, рабочее время, заблокированное
время.
"""

from datetime import time

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

from app.database import Base


class Client(Base):
    """
    Клиент.

    Создаётся автоматически при первом обращении к боту (/start).
    """

    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)

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
    name = Column(String(255), unique=True, nullable=False)
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
    status = Column(String(20), nullable=False, default='в ожидании')
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
    start_time = Column(Time, nullable=False, default=time(10))
    end_time = Column(Time, nullable=False, default=time(20))
    is_working = Column(Boolean, default=True)

    def __repr__(self):
        days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        return (
            f'<Рабочее время {days[self.day_of_week]} '
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
    reason = Column(String(255), nullable=True)

    def __repr__(self):
        return (
            f'<Нерабочее время {self.date} '
            f'{self.start_time}-{self.end_time}>'
        )
