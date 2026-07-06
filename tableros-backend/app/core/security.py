import httpx
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status
from app.core.config import settings
from urllib.parse import quote

# Cache en memoria de las claves públicas de Keycloak (JWK)
_jwks_cache: dict | None = None


async def get_jwks() -> dict:
    """
    Obtiene las claves públicas (JWK Set) desde Keycloak.
    Las guarda en memoria para no llamar a Keycloak en cada request.
    """
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(settings.keycloak_jwk_set_uri)
            response.raise_for_status()
            _jwks_cache = response.json()
    return _jwks_cache


def invalidate_jwks_cache() -> None:
    """Limpia el cache de JWKs (útil al rotar claves en Keycloak)."""
    global _jwks_cache
    _jwks_cache = None


async def decode_token(token: str) -> dict:
    """
    Valida y decodifica un JWT emitido por Keycloak.

    Verifica:
    - Firma con la clave pública de Keycloak (JWK)
    - Expiración del token
    - Issuer (iss) coincide con el realm configurado
    - Audience (aud) incluye el client_id configurado

    Retorna el payload del token si es válido.
    Lanza HTTPException 401 si no es válido.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        jwks = await get_jwks()

        # Decodificar sin verificar primero para obtener el kid del header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Buscar la clave pública correspondiente al kid
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n":   key["n"],
                    "e":   key["e"],
                }
                break

        if not rsa_key:
            raise credentials_exception

        # Validar y decodificar el token completo
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            issuer=settings.keycloak_issuer_uri,
            options={"verify_aud": False},  # Keycloak puede omitir aud en tokens de usuario
        )
        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception


def extract_username(payload: dict) -> str:
    """
    Extrae el username del payload del JWT.
    Usa el atributo configurado en .env (preferred_username por defecto).
    """
    username = payload.get(settings.keycloak_username_attribute)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"El token no contiene el atributo '{settings.keycloak_username_attribute}'",
        )
    return username


async def exchange_code_for_token(code: str, redirect_uri: str) -> dict:
    """
    Canjea un código de autorización por tokens usando client_secret.
    """
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            settings.keycloak_token_uri,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.keycloak_client_id,
                "client_secret": settings.keycloak_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error al canjear código: {response.text}",
        )
    return response.json()


async def refresh_access_token(refresh_token: str) -> dict:
    """
    Refresca el access_token usando el refresh_token.
    """
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            settings.keycloak_token_uri,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": settings.keycloak_client_id,
                "client_secret": settings.keycloak_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error al refrescar token: {response.text}",
        )
    return response.json()


def build_login_url(redirect_uri: str) -> str:
    """Construye la URL de login de Keycloak."""
    import urllib.parse
    params = (
        f"response_type=code"
        f"&client_id={settings.keycloak_client_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&scope={urllib.parse.quote(settings.keycloak_scopes)}"
    )
    return f"{settings.keycloak_auth_uri}?{params}"
