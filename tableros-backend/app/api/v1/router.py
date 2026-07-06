from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import dashboard  # 1. IMPORTAMOS EL NUEVO ENDPOINT

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(dashboard.router)  # 2. INCLUIMOS EL ROUTER DEL DASHBOARD

# Aquí irás agregando más routers conforme crezcas el proyecto:
# from app.api.v1.endpoints import usuarios
# api_router.include_router(usuarios.router)