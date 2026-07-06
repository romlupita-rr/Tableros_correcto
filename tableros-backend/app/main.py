from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import engine
from app.db.init_db import init_db
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación:
    - Al arrancar: crea tablas e inicializa bases de datos
    - Al apagar: cierra el engine de SQLAlchemy
    """
    # Startup
    init_db()  # Crea tablas via SQLAlchemy
    print("[App] Aplicación lista.")
    yield
    
    # Shutdown
    engine.dispose()
    print("[App] Conexiones cerradas.")

app = FastAPI(
    title="Backend API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# ── CORS DESBLOQUEADO COMPLETAMENTE PARA DESARROLLO ───────────────────────
# Se listan los puertos locales comunes y las cabeceras Axios para evitar fallos de red
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, OPTIONS sin restricciones
    allow_headers=["*"],  # Permite todas las cabeceras de Axios
)

# ── Middleware de autenticación/autorización ──────────────────
# app.add_middleware(AuthMiddleware)

# ── Routers ───────────────────────────────────────────────────
# Aquí se monta automáticamente api_router que ya contiene tu dashboard.py modificado
app.include_router(api_router)

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Endpoint público para verificar que el servidor está activo."""
    return {"status": "ok", "environment": settings.environment}