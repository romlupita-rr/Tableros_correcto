from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import mapped_column, Mapped
from typing import Optional
from app.db.session import Base


class Permiso(Base):
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    permiso: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
