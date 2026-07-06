from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ----------------------------------------------------------
    # Keycloak
    # ----------------------------------------------------------
    keycloak_server_url: str
    keycloak_realm: str
    keycloak_client_id: str
    keycloak_client_secret: str
    keycloak_issuer_uri: str
    keycloak_jwk_set_uri: str
    keycloak_username_attribute: str = "preferred_username"
    keycloak_scopes: str = "openid profile email roles"

    @property
    def keycloak_token_uri(self) -> str:
        return f"{self.keycloak_issuer_uri}/protocol/openid-connect/token"

    @property
    def keycloak_logout_uri(self) -> str:
        return f"{self.keycloak_issuer_uri}/protocol/openid-connect/logout"

    @property
    def keycloak_auth_uri(self) -> str:
        return f"{self.keycloak_issuer_uri}/protocol/openid-connect/auth"

    # ----------------------------------------------------------
    # Base de datos
    # ----------------------------------------------------------
    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def database_dsn(self) -> dict:
        """Formato dict para psycopg2 connect()"""
        return {
            "host": self.db_host,
            "port": self.db_port,
            "dbname": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
        }

    # ----------------------------------------------------------
    # Backend
    # ----------------------------------------------------------
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 5

    # ----------------------------------------------------------
    # Frontend (CORS)
    # ----------------------------------------------------------
    frontend_url: str = "http://localhost:3000"

    # ----------------------------------------------------------
    # Entorno
    # ----------------------------------------------------------
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Instancia única de Settings durante toda la vida de la app.
    Usar como dependencia en FastAPI:
        settings = Depends(get_settings)
    """
    return Settings()


# Instancia global para acceso directo
settings = get_settings()
