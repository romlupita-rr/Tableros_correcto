import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

# IMPORTACIONES COMPLETAMENTE ACTUALIZADAS (Sin la función eliminada)
from excel.leer_estado import (
    obtener_estados,
    obtener_regularidad_estados,
    obtener_nivel_desempeno_estados,
    obtener_top_planteles
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# =====================================================
# MODELO PARA PETICIONES DE ESTADOS
# =====================================================

class EstadosRequest(BaseModel):
    estados: list[str]


# =====================================================
# AUXILIAR: LIMPIEZA DE PARÁMETROS DE RED DE ESTADOS
# =====================================================

def limpiar_lista_query(estados: List[str], lista_estados: Optional[str] = None) -> List[str]:
    if lista_estados:
        return [e.strip() for e in lista_estados.split(",") if e.strip()]
    if estados and len(estados) == 1 and "," in estados[0]:
        return [e.strip() for e in estados[0].split(",") if e.strip()]
    return [e.strip() for e in estados if e.strip()]


# =====================================================
# 📊 ENDPOINTS NUEVOS: COMPARATIVA DE ESTADOS (SOLO ACTIVOS)
# =====================================================

@router.get("/periodos")
async def periodos_escolares():
    # Retorna únicamente el período solicitado
    return ["22526"]

@router.get("/catalogo-estados")
async def catalogo_estados():
    return {"error": None, "data": obtener_estados()}

@router.get("/estados/regularidad")
async def estados_regularidad(estados: List[str] = Query(default=[]), lista_estados: Optional[str] = None):
    try:
        lista_limpia = limpiar_lista_query(estados, lista_estados)
        return obtener_regularidad_estados(lista_limpia)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estados/desempeno")
async def estados_desempeno(estados: List[str] = Query(default=[]), lista_estados: Optional[str] = None):
    try:
        lista_limpia = limpiar_lista_query(estados, lista_estados)
        return obtener_nivel_desempeno_estados(lista_limpia)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estados/top-planteles")
async def estados_top_planteles(estados: List[str] = Query(default=[]), lista_estados: Optional[str] = None):
    try:
        lista_limpia = limpiar_lista_query(estados, lista_estados)
        return obtener_top_planteles(lista_limpia)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 🇲🇽 TU DASHBOARD NACIONAL ORIGINAL
# =====================================================

@router.get("/nacional")
async def get_dashboard_nacional():
    try:
        from excel.leer_nacional import obtener_metricas_nacionales
        return obtener_metricas_nacionales()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# 🏫 TU DASHBOARD PLANTEL ORIGINAL
# =====================================================

@router.get("/plantel")
async def get_dashboard_plantel():
    try:
        from excel.leer_plantel import obtener_metricas_nacionales
        return obtener_metricas_nacionales()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# 🔄 TU COMPARACIÓN DE PLANTELES ORIGINAL
# =====================================================

@router.get("/comparar")
@router.get("/comparacion")
async def get_comparacion_planteles(
    plantel1: str = Query(None, alias="p1"),
    plantel2: str = Query(None, alias="p2"),
    periodo: str = Query(None)
):
    if not plantel1 or not plantel2:
        return {
            "p1": {
                "matricula": 0,
                "promedio": 0,
                "regulares": 0,
                "regulares_pct": 0,
                "irregulares": 0,
                "irregulares_pct": 0
            },
            "p2": {
                "matricula": 0,
                "promedio": 0,
                "regulares": 0,
                "regulares_pct": 0,
                "irregulares": 0,
                "irregulares_pct": 0
            }
        }
    try:
        from excel.leer_plantel import obtener_comparacion_planteles
        return obtener_comparacion_planteles(
            cve_p1=plantel1,
            cve_p2=plantel2,
            periodo=periodo
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# 📈 TUS MÉTRICAS DE UN PLANTEL ORIGINAL
# =====================================================

@router.get("/metricas")
async def get_metricas_plantel(
    plant: str = Query(..., alias="plantel"),
    periodo: str = Query(None)
):
    try:
        from excel.leer_plantel import (
            CSV_ALUMNOS,
            calcular_metricas_plantel
        )
        df = pd.read_csv(
            CSV_ALUMNOS,
            low_memory=False
        )

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        if periodo and "periodoescolar" in df.columns:
            df["periodoescolar"] = (
                df["periodoescolar"]
                .astype(str)
                .str.strip()
            )

            df = df[
                df["periodoescolar"] == str(periodo).strip()
            ]

        return calcular_metricas_plantel(
            df,
            plant
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )