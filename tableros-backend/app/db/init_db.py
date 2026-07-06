from app.db.session import engine, Base

from app.models.usuario import Usuario  # noqa: F401
from app.models.rol import Rol  # noqa: F401
from app.models.permiso import Permiso  # noqa: F401
from app.models.usuario_rol import UsuarioRol  # noqa: F401
from app.models.rol_permiso import RolPermiso  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("[DB] Tablas verificadas/creadas correctamente.")
