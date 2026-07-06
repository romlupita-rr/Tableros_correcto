from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from app.db.session import Base


class UsuarioRol(Base):
    __tablename__ = "usuarios_roles"

    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    id_rol: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
