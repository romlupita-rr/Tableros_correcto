from sqlalchemy.orm import Session
from typing import Optional
from app.models.usuario import Usuario, UsuarioCreate
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[Usuario]:
        return (
            self.db.query(Usuario)
            .filter(Usuario.username == username)
            .first()
        )

    def get_by_keycloak_id(self, keycloak_id: str) -> Optional[Usuario]:
        return (
            self.db.query(Usuario)
            .filter(Usuario.keycloak_id == keycloak_id)
            .first()
        )

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def get_all(self, solo_activos: bool = False) -> list[Usuario]:
        query = self.db.query(Usuario)
        if solo_activos:
            query = query.filter(Usuario.estado == True)
        return query.order_by(Usuario.username).all()

    def create(self, data: UsuarioCreate) -> Usuario:
        nuevo = Usuario(
            nombre=data.nombre,
            a_paterno=data.a_paterno,
            a_materno=data.a_materno,
            correo_institucional=data.correo_institucional,
            username=data.username,
            keycloak_id=data.keycloak_id,
        )
        self.db.add(nuevo)
        self.db.flush()
        self.db.refresh(nuevo)
        return nuevo

    def create_from_payload(self, payload: dict) -> Usuario:
        correo = payload.get("email", "")
        keycloak_id = payload.get("sub")
        username = payload.get("preferred_username", "")

        existente = (
            self.db.query(Usuario)
            .filter(
                (Usuario.correo_institucional == correo)
                | (Usuario.keycloak_id == keycloak_id)
            )
            .first()
        )
        if existente:
            existente.keycloak_id = keycloak_id or existente.keycloak_id
            existente.username = username
            self.db.commit()
            self.db.refresh(existente)
            return existente

        nombre_completo = (payload.get("name") or "").strip()
        partes = nombre_completo.split(" ", 2)
        nombre = partes[0] if partes else username
        a_paterno = partes[1] if len(partes) > 1 else ""
        a_materno = partes[2] if len(partes) > 2 else None

        nuevo = Usuario(
            nombre=nombre,
            a_paterno=a_paterno,
            a_materno=a_materno,
            correo_institucional=correo,
            username=username,
            keycloak_id=keycloak_id,
        )
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def is_active(self, username: str) -> bool:
        result = (
            self.db.query(Usuario.estado)
            .filter(Usuario.username == username)
            .first()
        )
        return bool(result and result.estado)

    def get_roles(self, usuario_id: int) -> list[str]:
        return [
            r[0]
            for r in self.db.query(Rol.rol)
            .join(UsuarioRol, UsuarioRol.id_rol == Rol.id)
            .filter(UsuarioRol.id_usuario == usuario_id)
            .all()
        ]
