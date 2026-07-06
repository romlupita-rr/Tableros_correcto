from sqlalchemy.orm import Session
from typing import Optional
from app.models.rol import Rol


class RolRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, rol_id: int) -> Optional[Rol]:
        return self.db.query(Rol).filter(Rol.id == rol_id).first()

    def get_by_name(self, nombre: str) -> Optional[Rol]:
        return self.db.query(Rol).filter(Rol.rol == nombre).first()

    def get_all(self) -> list[Rol]:
        return self.db.query(Rol).order_by(Rol.rol).all()
