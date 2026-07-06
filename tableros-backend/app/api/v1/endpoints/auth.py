from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.db.session import get_db
from app.core.security import exchange_code_for_token, build_login_url, get_jwks
from app.core.jwt import create_access_token, decode_access_token
from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario import UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class LoginRequest(BaseModel):
    code: str
    redirectUri: str


class TokenResponse(BaseModel):
    accessToken: str
    expiresIn: int
    tokenType: str = "Bearer"
    user: dict


class RefreshResponse(BaseModel):
    accessToken: str
    expiresIn: int
    tokenType: str = "Bearer"
    user: dict


class LoginUrlResponse(BaseModel):
    loginUrl: str


def _build_user_payload(usuario, roles: list[str]) -> dict:
    return {
        "sub": usuario.keycloak_id or "",
        "id": usuario.id,
        "correo_institucional": usuario.correo_institucional,
        "username": usuario.username,
        "roles": roles,
    }


async def _decode_keycloak_id_token(id_token: str) -> dict:
    jwks = await get_jwks()
    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header.get("kid")

    rsa_key = None
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            break

    if not rsa_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró la clave pública de Keycloak",
        )

    try:
        payload = jwt.decode(
            id_token,
            rsa_key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,
                "verify_at_hash": False,
            },
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"id_token inválido: {str(e)}",
        )


@router.get("/login-url", response_model=LoginUrlResponse)
async def get_login_url():
    return LoginUrlResponse(
        loginUrl=build_login_url("http://localhost:8000/callback")
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    keycloak_tokens = await exchange_code_for_token(body.code, body.redirectUri)
    id_token = keycloak_tokens.get("id_token")

    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keycloak no devolvió id_token",
        )

    id_payload = await _decode_keycloak_id_token(id_token)

    repo = UsuarioRepository(db)
    sub = id_payload.get("sub")
    preferred_username = id_payload.get("preferred_username", "")
    if sub:
        usuario = repo.get_by_keycloak_id(sub)
    else:
        usuario = None
    if not usuario:
        usuario = repo.get_by_username(preferred_username)
    if not usuario:
        usuario = repo.create_from_payload(id_payload)

    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador",
        )

    if not usuario.keycloak_id and id_payload.get("sub"):
        usuario.keycloak_id = id_payload["sub"]
        db.flush()

    roles = repo.get_roles(usuario.id)
    user_payload = _build_user_payload(usuario, roles)

    access_token = create_access_token(user_payload)

    return TokenResponse(
        accessToken=access_token,
        expiresIn=5 * 60,
        user=user_payload,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido",
        )
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)

    usuario_id = payload.get("id")
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    repo = UsuarioRepository(db)
    usuario = repo.get_by_id(usuario_id)
    if not usuario or not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo o no encontrado",
        )

    roles = repo.get_roles(usuario.id)
    user_payload = _build_user_payload(usuario, roles)

    access_token = create_access_token(user_payload)

    return RefreshResponse(
        accessToken=access_token,
        expiresIn=5 * 60,
        user=user_payload,
    )


@router.get("/me", response_model=UsuarioResponse)
async def get_me(request: Request):
    return request.state.usuario
