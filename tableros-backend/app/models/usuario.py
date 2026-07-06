from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.db.session import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    a_paterno: Mapped[str] = mapped_column(String(100), nullable=False)
    a_materno: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    correo_institucional: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    keycloak_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    estado: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    fecha_modificacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    fecha_eliminacion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class UsuarioBase(BaseModel):
    nombre: str
    a_paterno: str
    a_materno: Optional[str] = None
    correo_institucional: EmailStr
    username: str


class UsuarioCreate(UsuarioBase):
    keycloak_id: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id: int
    keycloak_id: Optional[str] = None
    estado: bool
    fecha_creacion: datetime
    fecha_modificacion: datetime
    fecha_eliminacion: Optional[datetime] = None

    class Config:
        from_attributes = True
