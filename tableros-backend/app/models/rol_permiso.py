from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from app.db.session import Base


class RolPermiso(Base):
    __tablename__ = "roles_permisos"

    id_rol: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    id_permiso: Mapped[int] = mapped_column(Integer, ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True)
