from sqlalchemy.orm import Session
from typing import Optional
from app.models.permiso import Permiso
from app.models.usuario_rol import UsuarioRol
from app.models.rol_permiso import RolPermiso


class PermisoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, permiso_id: int) -> Optional[Permiso]:
        return self.db.query(Permiso).filter(Permiso.id == permiso_id).first()

    def get_by_name(self, nombre: str) -> Optional[Permiso]:
        return self.db.query(Permiso).filter(Permiso.permiso == nombre).first()

    def get_all(self) -> list[Permiso]:
        return self.db.query(Permiso).order_by(Permiso.permiso).all()

    def get_permisos_por_usuario(self, usuario_id: int) -> list[Permiso]:
        return (
            self.db.query(Permiso)
            .join(RolPermiso, RolPermiso.id_permiso == Permiso.id)
            .join(UsuarioRol, UsuarioRol.id_rol == RolPermiso.id_rol)
            .filter(UsuarioRol.id_usuario == usuario_id)
            .all()
        )

    def usuario_tiene_permiso(self, usuario_id: int, permiso_nombre: str) -> bool:
        return (
            self.db.query(Permiso)
            .join(RolPermiso, RolPermiso.id_permiso == Permiso.id)
            .join(UsuarioRol, UsuarioRol.id_rol == RolPermiso.id_rol)
            .filter(UsuarioRol.id_usuario == usuario_id)
            .filter(Permiso.permiso == permiso_nombre)
            .first()
        ) is not None
