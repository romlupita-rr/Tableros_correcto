from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.auth_service import get_current_user_from_jwt, verify_permission
from app.models.usuario import UsuarioResponse
from app.repositories.usuario_repository import UsuarioRepository
from app.db.session import SessionLocal

PUBLIC_PATHS = {
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/login-url",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware global que:
    1. Deja pasar las rutas públicas sin validación
    2. Extrae el Bearer token (JWT propio del backend)
    3. Decodifica el JWT y valida el usuario en BD
    4. Verifica permisos en BD
    5. Adjunta el usuario y sus roles al request.state
    """

    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header requerido"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]

        db = SessionLocal()
        try:
            usuario = await get_current_user_from_jwt(token, db)
            verify_permission(usuario, request, db)

            repo = UsuarioRepository(db)
            roles = repo.get_roles(usuario.id)

            request.state.usuario = UsuarioResponse.model_validate(usuario)
            request.state.roles = roles

        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Error interno: {str(exc)}"},
            )
        finally:
            db.close()

        return await call_next(request)
