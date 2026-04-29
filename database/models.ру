from sqlalchemy import BigInteger, String, Boolean, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user ID
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    birth_date: Mapped[str | None] = mapped_column(String(10), nullable=True)  # DD.MM.YYYY

    belova_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    psychomatrix: Mapped[str | None] = mapped_column(String(512), nullable=True)  # JSON string

    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    preferred_time: Mapped[str | None] = mapped_column(String(256), nullable=True)
    contact_info: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, confirmed, done
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
