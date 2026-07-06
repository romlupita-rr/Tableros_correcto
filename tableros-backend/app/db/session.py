from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from app.core.config import settings

# ── Engine principal ──────────────────────────────────────────
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=5,           # Conexiones permanentes en el pool
    max_overflow=10,       # Conexiones extra permitidas bajo carga
    pool_pre_ping=True,    # Verifica que la conexión sigue viva antes de usarla
    echo=settings.debug,   # Loguea el SQL generado en modo desarrollo
)

# ── Fábrica de sesiones ───────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ── Base para los modelos ORM ─────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependencia para FastAPI ──────────────────────────────────
def get_db():
    """
    Generador para inyectar la sesión en endpoints y servicios.

    Uso en endpoint:
        def mi_endpoint(db: Session = Depends(get_db)):
            ...

    Maneja commit/rollback/close automáticamente.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
