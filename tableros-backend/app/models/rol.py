from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import mapped_column, Mapped
from typing import Optional
from app.db.session import Base


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rol: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
