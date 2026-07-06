from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.jwt import decode_access_token
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.permiso_repository import PermisoRepository
from app.models.usuario import Usuario


async def get_current_user_from_jwt(token: str, db: Session) -> Usuario:
    """
    Decodifica el JWT propio del backend, valida que el usuario exista
    y esté activo en BD.
    """
    payload = decode_access_token(token)

    usuario_id = payload.get("id")
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    repo = UsuarioRepository(db)
    usuario = repo.get_by_id(usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador",
        )
    return usuario


def _extract_resource(path: str) -> str:
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
        return parts[2]
    return parts[-1] if parts else path


def _map_method_to_action(method: str) -> str:
    mapping = {
        "GET": "read",
        "POST": "write",
        "PUT": "write",
        "PATCH": "write",
        "DELETE": "delete",
    }
    return mapping.get(method, method.lower())


def verify_permission(usuario: Usuario, request: Request, db: Session) -> None:
    resource = _extract_resource(request.url.path)
    action = _map_method_to_action(request.method)
    required_permission = f"{resource}.{action}"

    repo = PermisoRepository(db)
    has_perm = repo.usuario_tiene_permiso(usuario.id, required_permission)

    if not has_perm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sin permisos para {action} {resource}",
        )
