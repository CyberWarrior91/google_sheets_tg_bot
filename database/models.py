from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List


from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    access_token: Mapped[str] = mapped_column(Text, default=None, nullable=True)
    spreadsheets: Mapped[List[Spreadsheet]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Spreadsheet(Base):
    __tablename__ = "spreadsheet"

    google_unique_id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    sheets: Mapped[List[Sheet]] = relationship(back_populates="spreadsheet", cascade="all, delete-orphan")
    user_telegram_id: Mapped[int] = mapped_column(ForeignKey("user.telegram_id"))
    user: Mapped[User] = relationship(back_populates="spreadsheets")

    __mapper_args__ = {
        "polymorphic_identity": "spreadsheet",
    }

class Sheet(Base):
    __tablename__ = "sheet"

    id: Mapped[int] = mapped_column(primary_key=True)
    google_unique_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(30))
    spreadsheet_id: Mapped[str] = mapped_column(ForeignKey("spreadsheet.google_unique_id"))
    spreadsheet: Mapped[Spreadsheet] = relationship(back_populates="sheets")

    __mapper_args__ = {
        "polymorphic_identity": "sheet",
    }
