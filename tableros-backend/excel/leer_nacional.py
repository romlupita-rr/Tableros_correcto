import traceback
import numpy as np
import pandas as pd
from pathlib import Path


# =====================================================
# 🔥 LIMPIEZA SEGURA PARA JSON
# =====================================================
def limpiar_nan(data):
    if isinstance(data, list):
        return [limpiar_nan(i) for i in data]

    if isinstance(data, dict):
        return {k: limpiar_nan(v) for k, v in data.items()}

    try:
        if pd.isna(data):
            return None
    except Exception:
        pass

    if isinstance(data, (np.integer, np.floating)):
        return data.item()

    return data


# =====================================================
# 🔥 NUEVO: PERIODOS ESCOLARES (CON ARCHIVO FIJO)
# =====================================================
def obtener_periodos_escolares():

    try:
        BASE_DIR = Path(__file__).resolve().parent
        BACKEND_DIR = BASE_DIR.parent
        EXCEL_DIR = BACKEND_DIR / "excel"

        ruta_modulos = EXCEL_DIR / "20260602-alumnomodulo .csv"

        if not ruta_modulos.exists():
            ruta_modulos = EXCEL_DIR / "20260602-alumnomodulo .csv"

        if not ruta_modulos.exists():
            return []

        df = pd.read_csv(
            ruta_modulos,
            encoding="latin1",
            low_memory=True
        )

        df.columns = df.columns.str.strip().str.lower()

        if "periodoescolar" not in df.columns:
            return []

        return (
            df["periodoescolar"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

    except Exception:
        print("❌ ERROR periodos escolares:")
        print(traceback.format_exc())
        return []


# =====================================================
# 🔥 REGULARIDAD HISTÓRICA
# =====================================================
def calcular_regularidad_historica(ruta_modulos):

    if ruta_modulos is None or not ruta_modulos.exists():
        return []

    try:
        df = pd.read_csv(
            ruta_modulos,
            encoding="latin1",
            usecols=["periodoescolar", "matricula", "califfinal"],
            low_memory=True
        )

        df.columns = df.columns.str.strip().str.lower()

        df["califfinal"] = pd.to_numeric(
            df["califfinal"],
            errors="coerce"
        )

        df["periodoescolar"] = (
            df["periodoescolar"]
            .astype(str)
            .str.strip()
        )

        df_22526 = df[df["periodoescolar"] == "22526"]

        if df_22526.empty:
            return [
                {
                    "periodo": "22526",
                    "tipo": "Real",
                    "regularidad": 0
                },
                {
                    "periodo": "12627",
                    "tipo": "Proyección",
                    "regularidad": 0
                }
            ]

        promedio = (
            df_22526
            .groupby("matricula")["califfinal"]
            .mean()
            .reset_index()
        )

        total = promedio["matricula"].nunique()

        regulares = (
            promedio[promedio["califfinal"] >= 7]
            ["matricula"]
            .nunique()
        )

        porcentaje = (
            round((regulares / total) * 100, 2)
            if total else 0
        )

        return [
            {
                "periodo": "22526",
                "tipo": "Real",
                "regularidad": porcentaje
            },
            {
                "periodo": "12627",
                "tipo": "Proyección",
                "regularidad": porcentaje
            }
        ]

    except Exception:
        print("❌ ERROR regularidad histórica:")
        print(traceback.format_exc())
        return []


# =====================================================
# 🔥 PROYECCIÓN FUTURA DE APROVECHAMIENTO
# =====================================================
def calcular_proyeccion_aprovechamiento(ruta_modulos):

    if ruta_modulos is None or not ruta_modulos.exists():
        return []

    try:
        df = pd.read_csv(
            ruta_modulos,
            encoding="latin1",
            usecols=[
                "periodoescolar",
                "matricula",
                "califfinal"
            ],
            low_memory=True
        )

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        df["califfinal"] = pd.to_numeric(
            df["califfinal"],
            errors="coerce"
        )

        df["periodoescolar"] = (
            df["periodoescolar"]
            .astype(str)
            .str.strip()
        )

        # =========================
        # REAL 22526
        # =========================
        real_df = df[
            df["periodoescolar"] == "22526"
        ]

        real_prom = (
            round(real_df["califfinal"].mean(), 2)
            if not real_df.empty
            else 0
        )

        # =========================
        # PROYECCIÓN 12627
        # =========================
        proj_df = df[
            df["periodoescolar"] == "12627"
        ]

        if not proj_df.empty:
            proj_prom = round(
                proj_df["califfinal"].mean(),
                2
            )
        else:
            proj_prom = round(
                real_prom * 1.02,
                2
            )

        return [
            {
                "periodo": "22526",
                "tipo": "Real",
                "promedio": real_prom
            },
            {
                "periodo": "12627",
                "tipo": "Proyección",
                "promedio": proj_prom
            }
        ]

    except Exception:
        print("❌ ERROR proyección:")
        print(traceback.format_exc())
        return []


# =====================================================
# 🔥 DASHBOARD NACIONAL
# =====================================================
def obtener_metricas_nacionales():

    try:
        BASE_DIR = Path(__file__).resolve().parent
        BACKEND_DIR = BASE_DIR.parent
        EXCEL_DIR = BACKEND_DIR / "excel"

        ruta_alumnos = EXCEL_DIR / "20260602-alumno.csv"
        ruta_planteles = EXCEL_DIR / "20260602-planteles.csv"
        ruta_catalogo = EXCEL_DIR / "Catalogo_entidades.csv"
        ruta_modulos = EXCEL_DIR / "20260602-alumnomodulo .csv"
        ruta_carreras = EXCEL_DIR / "20260602-carreras.csv"

        # =========================
        # LECTURA ARCHIVOS
        # =========================
        df = pd.read_csv(ruta_alumnos, low_memory=False)
        df_planteles = pd.read_csv(ruta_planteles, low_memory=False)
        df_catalogo = pd.read_csv(
            ruta_catalogo,
            sep=";",
            encoding="latin1",
            low_memory=False
        )
        df_carreras = pd.read_csv(ruta_carreras, low_memory=False)

        df.columns = df.columns.str.strip().str.lower()
        df_planteles.columns = df_planteles.columns.str.strip().str.lower()
        df_catalogo.columns = df_catalogo.columns.str.strip().str.lower()
        df_carreras.columns = (
            df_carreras.columns
            .str.replace('"', "")
            .str.strip()
            .str.lower()
        )

        if "cveplanestudio" in df.columns:
            df["cveplanestudio"] = (
                df["cveplanestudio"]
                .astype(str)
                .str.strip()
            )

        if "cveplanestudio" in df_carreras.columns:
            df_carreras["cveplanestudio"] = (
                df_carreras["cveplanestudio"]
                .astype(str)
                .str.strip()
            )
            df_carreras["plan_match"] = (
                df_carreras["cveplanestudio"]
                .str.replace("T$", "", regex=True)
            )

        # =========================
        # CALIFICACIÓN
        # =========================
        if "promg" in df.columns:
            df["califfinal"] = pd.to_numeric(df["promg"], errors="coerce")
        elif "cspromgral" in df.columns:
            df["califfinal"] = pd.to_numeric(df["cspromgral"], errors="coerce")
        else:
            df["califfinal"] = pd.NA

        # =========================
        # VALIDACIÓN
        # =========================
        for col in ["matricula", "cveunidadmin", "cveentidad"]:
            if col not in df.columns:
                return {"error": f"Falta columna {col}"}

        # =========================
        # KPIs
        # =========================
        total_alumnos = int(df["matricula"].nunique())
        total_planteles = int(df_planteles["cveunidadmin"].nunique())
        regulares = int(df[df["califfinal"] >= 7]["matricula"].nunique())
        irregulares = int(df[df["califfinal"] < 7]["matricula"].nunique())
        promedio_nacional = round(df["califfinal"].mean(), 2)

        # =========================
        # DESEMPEÑO POR ESTADO
        # =========================
        df["cveentidad"] = df["cveentidad"].astype(str).str.strip()
        df_catalogo["cveentidad"] = df_catalogo["cveentidad"].astype(str).str.strip()

        # Se eliminan los estados 0, 39 y 40 (contemplando formato texto y float)
        df_filtrado_desempeno = df[~df["cveentidad"].isin(["0", "39", "40", "0.0", "39.0", "40.0"])]

        df_prom = (
            df_filtrado_desempeno.groupby("cveentidad")
            .agg(promedio=("califfinal", "mean"), alumnos=("matricula", "nunique"))
            .reset_index()
        )
        df_prom["promedio"] = df_prom["promedio"].round(2)

        entidades = (
            df_catalogo[["cveentidad", "nombreentidad"]]
            .drop_duplicates()
        )

        # Se realiza un inner join para mantener únicamente los estados procesados y válidos
        df_final = df_prom.merge(entidades, on="cveentidad", how="inner")
        df_final["promedio"] = df_final["promedio"].fillna(0)
        df_final["alumnos"] = df_final["alumnos"].fillna(0)

        desempeno_json = (
            df_final.sort_values("promedio", ascending=False).to_dict("records")
        )

        # =========================
        # REGULARIDAD E IRREGULARIDAD ESTATAL
        # =========================
        # Se elimina el estado 0 antes de procesar regularidades
        df_filtrado_regularidad = df[~df["cveentidad"].isin(["0", "0.0"])]
        
        df_regularidad = df_filtrado_regularidad.copy()
        df_regularidad["es_regular"] = df_regularidad["califfinal"] >= 7

        regularidad_estado = (
            df_regularidad.groupby("cveentidad")
            .agg(
                total_alumnos=("matricula", "nunique"),
                regulares=("es_regular", "sum")
            )
            .reset_index()
        )
        regularidad_estado["irregulares"] = (
            regularidad_estado["total_alumnos"] - regularidad_estado["regulares"]
        )
        regularidad_estado["regulares_pct"] = (
            (regularidad_estado["regulares"] / regularidad_estado["total_alumnos"] * 100)
            .round(2)
        )
        regularidad_estado["irregulares_pct"] = (
            (regularidad_estado["irregulares"] / regularidad_estado["total_alumnos"] * 100)
            .round(2)
        )
        regularidad_estado = regularidad_estado.merge(
            entidades,
            on="cveentidad",
            how="left"
        )
        regularidad_estado = regularidad_estado.sort_values(
            "regulares_pct",
            ascending=False
        )
        regularidad_estatal = regularidad_estado.to_dict("records")

        # =========================
        # GRÁFICAS EXISTENTES
        # =========================
        regularidad_historica = calcular_regularidad_historica(ruta_modulos)
        proyeccion_aprovechamiento = calcular_proyeccion_aprovechamiento(ruta_modulos)

        # =========================
        # TOP 5 CARRERAS
        # =========================
        top_carreras = {"mejores": [], "peores": []}

        try:
            if "califfinal" not in df.columns:
                if "promg" in df.columns:
                    df["califfinal"] = pd.to_numeric(df["promg"], errors="coerce")
                elif "cspromgral" in df.columns:
                    df["califfinal"] = pd.to_numeric(df["cspromgral"], errors="coerce")
                else:
                    df["califfinal"] = pd.NA

            df["califfinal"] = pd.to_numeric(df["califfinal"], errors="coerce")
            df = df.dropna(subset=["califfinal", "cveplanestudio"])

            df["cveplanestudio"] = (
                df["cveplanestudio"]
                .astype(str)
                .str.upper()
                .str.strip()
                .str.replace('"', "", regex=False)
                .str.replace("\xa0", "", regex=False)
            )

            if len(df) == 0:
                print("⚠️ DF vacío después de limpieza TOP CARRERAS")

            carreras_prom = (
                df.groupby("cveplanestudio")
                .agg(
                    promedio=("califfinal", "mean"),
                    alumnos=("matricula", "nunique")
                )
                .reset_index()
            )

            carreras_prom["promedio"] = carreras_prom["promedio"].round(2)
            carreras_prom["carrera"] = carreras_prom["cveplanestudio"]

            top_carreras["mejores"] = (
                carreras_prom.sort_values("promedio", ascending=False)
                .head(5)[["carrera", "promedio"]]
                .to_dict("records")
            )
            top_carreras["peores"] = (
                carreras_prom.sort_values("promedio", ascending=True)
                .head(5)[["carrera", "promedio"]]
                .to_dict("records")
            )
        except Exception:
            print("❌ ERROR EN TOP CARRERAS")
            print(traceback.format_exc())

        # =========================
        # TOP PLANTELES
        # =========================
        top_planteles = {
            "mejores": [],
            "peores": []
        }

        try:
            planteles_prom = (
                df.groupby("cveunidadmin")
                .agg(
                    promedio=("califfinal", "mean"),
                    alumnos=("matricula", "nunique")
                )
                .reset_index()
            )

            planteles_prom["promedio"] = planteles_prom["promedio"].round(2)

            catalogo_planteles = (
                df_planteles[["cveunidadmin", "descripcion"]]
                .drop_duplicates()
            )

            planteles_prom = planteles_prom.merge(
                catalogo_planteles,
                on="cveunidadmin",
                how="left"
            )

            # Mapeo para identificar el estado al que pertenece cada plantel
            relacion_plantel_estado = df[["cveunidadmin", "cveentidad"]].drop_duplicates()
            relacion_plantel_estado = relacion_plantel_estado.merge(entidades, on="cveentidad", how="left")
            
            planteles_prom = planteles_prom.merge(
                relacion_plantel_estado[["cveunidadmin", "nombreentidad"]].drop_duplicates(subset=["cveunidadmin"]),
                on="cveunidadmin",
                how="left"
            )
            planteles_prom["estado"] = planteles_prom["nombreentidad"].fillna("Desconocido")

            planteles_prom["aprovechamiento"] = (
                (planteles_prom["promedio"] / 10) * 100
            ).round(0)

            # Se añade la columna "estado" al diccionario de salida del top
            top_planteles["mejores"] = (
                planteles_prom
                .sort_values("promedio", ascending=False)
                .head(5)[["cveunidadmin", "descripcion", "estado", "promedio", "aprovechamiento"]]
                .to_dict("records")
            )

            top_planteles["peores"] = (
                planteles_prom
                .sort_values("promedio", ascending=True)
                .head(5)[["cveunidadmin", "descripcion", "estado", "promedio", "aprovechamiento"]]
                .to_dict("records")
            )
        except Exception:
            print("❌ ERROR TOP PLANTELES")
            print(traceback.format_exc())

        # =========================
        # 🔥 TOP 10 DEMANDA (CORREGIDO)
        # =========================
        top_demanda = []

        try:
            df_demanda = df.copy()

            # total alumnos por estado
            total_estado = (
                df_demanda.groupby("cveentidad")
                .agg(total_alumnos=("matricula", "nunique"))
                .reset_index()
            )

            # alumnos por estado + carrera
            demanda = (
                df_demanda.groupby(["cveentidad", "cveplanestudio"])
                .agg(alumnos=("matricula", "nunique"))
                .reset_index()
            )

            # unir totales
            demanda = demanda.merge(total_estado, on="cveentidad", how="left")

            # evitar división por 0
            demanda["total_alumnos"] = demanda["total_alumnos"].replace(0, 1)

            # índice de demanda
            demanda["indice_demanda"] = (
                (demanda["alumnos"] / demanda["total_alumnos"]) * 100
            ).round(2)

            # catálogo de estados
            entidades = (
                df_catalogo[["cveentidad", "nombreentidad"]]
                .drop_duplicates()
            )

            demanda = demanda.merge(entidades, on="cveentidad", how="left")

            # limpiar nulls
            demanda["nombreentidad"] = demanda["nombreentidad"].fillna("Desconocido")

            demanda["cveplanestudio"] = demanda["cveplanestudio"].fillna("N/A")

            # TOP 10 REAL
            top_demanda = (
                demanda.sort_values("indice_demanda", ascending=False)
                .head(10)[
                    ["nombreentidad", "cveplanestudio", "indice_demanda"]
                ]
                .to_dict("records")
            )

        except Exception:
            print("❌ ERROR TOP DEMANDA")
            print(traceback.format_exc())

        # =========================
        # RESPONSE FINAL
        # =========================
        return limpiar_nan({
            "periodos_escolares": obtener_periodos_escolares(),
            "matricula_total": f"{total_alumnos:,}",
            "regulares": f"{regulares:,}",
            "irregulares": f"{irregulares:,}",
            "planteles": str(total_planteles),
            "promedio_nacional": promedio_nacional,
            "desempeno_estatal": desempeno_json,
            "regularidad_historica": regularidad_historica,
            "proyeccion_aprovechamiento": proyeccion_aprovechamiento,
            "regularidad_estatal": regularidad_estatal,
            "top_carreras": top_carreras,
            "top_planteles": top_planteles,
            "top_demanda_carreras_estado": top_demanda
        })

    except Exception:
        print("❌ ERROR BACKEND:")
        print(traceback.format_exc())
        return {"error": "backend error"}