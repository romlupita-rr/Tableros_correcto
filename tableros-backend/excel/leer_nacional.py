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

        # =========================
        # LECTURA OPCIONAL: MÓDULOS (alumnomodulo)
        # =========================
        df_mod = pd.DataFrame()
        try:
            if ruta_modulos.exists():
                df_mod = pd.read_csv(ruta_modulos, encoding="latin1", low_memory=False)
            else:
                # Si no existe el archivo de módulos, intentamos reutilizar el dataframe de alumnos
                df_mod = df.copy()
        except Exception:
            print("⚠️ No se pudo leer archivo de módulos, se usará datos de alumnos:", ruta_modulos)
            df_mod = df.copy()

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
        # KPIs (CORREGIDOS PARA MATRICULA REAL)
        # =========================
        
        # 1. Cálculo de status desde módulos (archivo base)
        def obtener_nota_minima(cve):
            try:
                anio = int(str(cve)[:4])
                return 7 if anio <= 2018 else 6
            except:
                return 6

        df_mod["califfinal"] = pd.to_numeric(df_mod["califfinal"], errors="coerce")
        df_mod["nota_minima"] = df_mod["cvemodeloeducativo"].apply(obtener_nota_minima)
        df_mod["es_aprobado"] = df_mod["califfinal"] >= df_mod["nota_minima"]

        # Creamos una serie de verdad: por matrícula, ¿es regular?
        # Si un alumno NO está en módulos, el fillna(False) lo marca como irregular
        status_por_alumno = df_mod.groupby("matricula")["es_aprobado"].min()
        
        # 2. Cruce con el archivo original para respetar los 297,569
        df_status = status_por_alumno.to_frame(name="es_regular").reset_index()
        
        # Hacemos left join para conservar TODOS los alumnos de df
        df_final_kpi = df.merge(df_status, on="matricula", how="left")
        
        # Si es NaN en 'es_regular', significa que no está en el archivo de módulos -> es irregular
        df_final_kpi["es_regular"] = df_final_kpi["es_regular"].fillna(False)

        # 3. Asignación de variables
        total_alumnos = int(df_final_kpi["matricula"].nunique())
        regulares = int(df_final_kpi["es_regular"].sum())
        irregulares = total_alumnos - regulares
        
        # Promedio (basado en el archivo alumno, o si prefieres de módulos, indícame)
        promedio_nacional = round(df["califfinal"].mean(), 2) 
        
        total_planteles = int(df_planteles["cveunidadmin"].nunique())
        
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
        # 🛠️ TOP 5 CARRERAS (SOLUCIÓN REAL BASADA EN TU CSV)
        # =========================
        top_carreras = {"mejores": [], "peores": []}
        try:
            df["califfinal"] = pd.to_numeric(df["califfinal"], errors="coerce")
            df_carreras_clean = df.dropna(subset=["califfinal", "cveplanestudio"]).copy()
            
            df_carreras_clean["cveplanestudio"] = (
                df_carreras_clean["cveplanestudio"]
                .astype(str)
                .str.upper()
                .str.strip()
            )

            mapa_exacto = {}
            mapa_raiz = {} # Para emparejar por los primeros 4 caracteres (ej: RECL25 -> RECL)

            # 🔄 LECTURA DEL CSV EVITANDO EL ENCABEZADO CORRUPTO
            if "ruta_carreras" in locals() and ruta_carreras.exists():
                try:
                    # Saltamos la primera línea rota (skiprows=1) y forzamos nombres limpios
                    df_cat = pd.read_csv(
                        ruta_carreras, 
                        skiprows=1, 
                        names=["modelo", "cve", "descripcion", "descorta"], 
                        encoding="latin1",
                        sep=","
                    )
                    
                    for _, row in df_cat.iterrows():
                        cve_original = str(row["cve"]).upper().strip()
                        desc = str(row["descripcion"]).strip()
                        
                        if cve_original and cve_original != "NAN":
                            # Guardamos coincidencia exacta por si acaso
                            mapa_exacto[cve_original] = desc
                            
                            # Guardamos por los primeros 4 caracteres (Raíz de la carrera)
                            if len(cve_original) >= 4:
                                raiz = cve_original[:4]
                                mapa_raiz[raiz] = desc
                except Exception as e:
                    print(f"⚠️ No se pudo leer el CSV de carreras: {e}")

            # Agrupamos los alumnos y calculamos promedios
            carreras_prom = (
                df_carreras_clean.groupby("cveplanestudio")
                .agg(promedio=("califfinal", "mean"))
                .reset_index()
            )
            carreras_prom["promedio"] = carreras_prom["promedio"].round(2)
            
            # 🔍 FUNCIÓN INTELEGENTE DE TRADUCCIÓN
            def obtener_nombre_carrera(cve):
                cve_clean = str(cve).upper().strip()
                if not cve_clean or cve_clean == "NAN":
                    return cve
                
                # 1. Intentar encontrar la clave exacta (ej: ASDI08T)
                if cve_clean in mapa_exacto:
                    return mapa_exacto[cve_clean]
                
                # 2. Intentar buscar por la raíz de 4 letras (ej: RECL18 -> extrae RECL -> encuentra RECL25)
                if len(cve_clean) >= 4:
                    raiz_alumno = cve_clean[:4]
                    if raiz_alumno in mapa_raiz:
                        return mapa_raiz[raiz_alumno]
                
                # 3. Búsqueda por aproximación de subcadenas si todo lo demás falla
                for k, v in mapa_exacto.items():
                    if k.startswith(cve_clean) or cve_clean.startswith(k):
                        return v
                        
                return cve # Si de plano no está en tu Excel, deja la clave para no romper el flujo

            # Reemplazamos las claves por las descripciones reales encontradas
            carreras_prom["carrera"] = carreras_prom["cveplanestudio"].apply(obtener_nombre_carrera)
            
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

     # =====================================================================
        # 🏢 TOP PLANTELES CORREGIDO (SOLO PROMEDIO, SIN PORCENTAJES)
        # =====================================================================
        top_planteles = {
            "mejores": [],
            "peores": []
        }

        try:
            # 1. Limpieza de claves y conversión a numérico en el df de alumnos
            df["cveunidadmin"] = df["cveunidadmin"].astype(str).str.strip()
            df["califfinal"] = pd.to_numeric(df["califfinal"], errors="coerce")
            df_clean = df.dropna(subset=["califfinal", "cveunidadmin"]).copy()

            # 2. Agrupación y cálculo de promedios por plantel (se descartan porcentajes)
            planteles_prom = (
                df_clean.groupby("cveunidadmin")
                .agg(promedio=("califfinal", "mean"))
                .reset_index()
            )
            planteles_prom["promedio"] = planteles_prom["promedio"].round(2)

            # 3. Homologar tipos de datos en los catálogos para evitar fallos de cruce
            df_planteles_clean = df_planteles.copy()
            df_planteles_clean["cveunidadmin"] = df_planteles_clean["cveunidadmin"].astype(str).str.strip()
            df_planteles_clean["cveentidad"] = pd.to_numeric(df_planteles_clean["cveentidad"], errors="coerce")

            entidades_clean = entidades.copy()
            entidades_clean["cveentidad"] = pd.to_numeric(entidades_clean["cveentidad"], errors="coerce")
            entidades_clean["nombreentidad"] = entidades_clean["nombreentidad"].astype(str).str.strip()

            # 4. Vincular el plantel a su estado usando EXCLUSIVAMENTE los catálogos oficiales
            mapeo_geografico = df_planteles_clean.merge(entidades_clean, on="cveentidad", how="left")

            # 5. Filtro de exclusión estricto para Oficinas Nacionales y Servicio Exterior
            mapeo_geografico = mapeo_geografico[
                (~mapeo_geografico["nombreentidad"].str.upper().str.contains("OF.NACIONALES|OFICINAS NACIONALES", na=False)) &
                (~mapeo_geografico["descripcion"].str.upper().str.contains("OF.NACIONALES|SERVICIO EXTERIOR", na=False)) &
                (mapeo_geografico["cveentidad"] != 0)
            ]

            # Reducimos a las columnas necesarias eliminando duplicados redundantes
            catalogo_final = mapeo_geografico[["cveunidadmin", "descripcion", "nombreentidad"]].drop_duplicates(subset=["cveunidadmin"])

            # 6. Cruzar los promedios con nuestro catálogo limpio
            planteles_prom = planteles_prom.merge(catalogo_final, on="cveunidadmin", how="inner")
            planteles_prom["estado"] = planteles_prom["nombreentidad"].fillna("Desconocido")

            # 7. Asignación final de los diccionarios con las columnas requeridas (Solo Promedio)
            top_planteles["mejores"] = (
                planteles_prom
                .sort_values("promedio", ascending=False)
                .head(5)[["cveunidadmin", "descripcion", "estado", "promedio"]]
                .to_dict("records")
            )

            top_planteles["peores"] = (
                planteles_prom
                .sort_values("promedio", ascending=True)
                .head(5)[["cveunidadmin", "descripcion", "estado", "promedio"]]
                .to_dict("records")
            )

        except Exception:
            print("❌ ERROR TOP PLANTELES")
            print(traceback.format_exc())
     # =====================================================================
        # 🔥 TOP 10 DEMANDA POR ESTADO (10 ESTADOS Y CARRERAS COMPLETAMENTE ÚNICAS)
        # =====================================================================
        top_demanda = []

        try:
            # 1. Limpieza inicial de datos de alumnos
            df_demanda = df.dropna(subset=["matricula", "cveplanestudio"]).copy()
            df_demanda["cveentidad"] = pd.to_numeric(df_demanda["cveentidad"], errors="coerce")
            df_demanda["cveplanestudio"] = df_demanda["cveplanestudio"].astype(str).str.upper().str.strip()

            # 2. Catálogo de carreras con solución al encabezado corrupto
            mapa_exacto = {}
            mapa_raiz = {}

            if "ruta_carreras" in locals() and ruta_carreras.exists():
                try:
                    df_cat = pd.read_csv(
                        ruta_carreras, 
                        skiprows=1, 
                        names=["modelo", "cve", "descripcion", "descorta"], 
                        encoding="latin1",
                        sep=","
                    )
                    for _, row in df_cat.iterrows():
                        cve_original = str(row["cve"]).upper().strip()
                        desc = str(row["descripcion"]).strip()
                        
                        if cve_original and cve_original != "NAN":
                            mapa_exacto[cve_original] = desc
                            if len(cve_original) >= 4:
                                mapa_raiz[cve_original[:4]] = desc
                except Exception as e:
                    print(f"⚠️ No se pudo leer el CSV de carreras en Demanda: {e}")

            # Función interna de traducción de claves a descripciones
            def obtener_nombre_carrera(cve):
                cve_clean = str(cve).upper().strip()
                if not cve_clean or cve_clean in ["NAN", "N/A"]:
                    return cve
                if cve_clean in mapa_exacto:
                    return mapa_exacto[cve_clean]
                if len(cve_clean) >= 4:
                    raiz_alumno = cve_clean[:4]
                    if raiz_alumno in mapa_raiz:
                        return mapa_raiz[raiz_alumno]
                return cve

            # 3. Limpieza del catálogo de estados (Exclusión de Oficinas Nacionales y Servicio Exterior)
            entidades_clean = entidades.copy()
            entidades_clean["cveentidad"] = pd.to_numeric(entidades_clean["cveentidad"], errors="coerce")
            entidades_clean["nombreentidad"] = entidades_clean["nombreentidad"].astype(str).str.strip()
            
            entidades_clean = entidades_clean[
                (~entidades_clean["nombreentidad"].str.upper().str.contains("OF.NACIONALES|OFICINAS NACIONALES|SERVICIO EXTERIOR MEXICANO", na=False)) &
                (entidades_clean["cveentidad"] != 0)
            ]

            # 4. Agrupar por Estado + Carrera para contar alumnos únicos inscritos
            # CAMBIO 1: Calculamos el total nacional de alumnos únicos para que el porcentaje sea lógico
            total_nacional = df_demanda["matricula"].nunique()
            if total_nacional == 0:
                total_nacional = 1

            demanda = (
                df_demanda.groupby(["cveentidad", "cveplanestudio"])
                .agg(alumnos=("matricula", "nunique"))
                .reset_index()
            )

            # CAMBIO 2: El índice de demanda ahora representa el impacto sobre la matrícula nacional 
            # (A mayor volumen de alumnos, mayor será el porcentaje de forma ascendente)
            demanda["indice_demanda"] = ((demanda["alumnos"] / total_nacional) * 100).round(2)

            # Cruzar con el catálogo de estados limpio
            demanda = demanda.merge(entidades_clean[["cveentidad", "nombreentidad"]], on="cveentidad", how="inner")
            demanda = demanda.rename(columns={"nombreentidad": "estado"})

            # Traducir claves de carreras a las descripciones reales del catálogo
            demanda["carrera"] = demanda["cveplanestudio"].apply(obtener_nombre_carrera)

            # 5. FILTRAR PARA QUE NO SE REPITAN ESTADOS NI CARRERAS EN EL TOP 10
            # Ordenamos de mayor a menor volumen absoluto de alumnos
            demanda_ordenada = demanda.sort_values("alumnos", ascending=False)
            
            estados_vistos = set()
            carreras_vistas = set()
            top_final = []

            for _, row in demanda_ordenada.iterrows():
                estado_actual = row["cveentidad"]
                carrera_actual = row["carrera"]
                
                # Regla estricta: Solo agregamos si el estado es nuevo Y la carrera no ha salido antes
                if estado_actual not in estados_vistos and carrera_actual not in carreras_vistas:
                    top_final.append(row)
                    estados_vistos.add(estado_actual)
                    carreras_vistas.add(carrera_actual)
                
                # Nos detenemos al juntar los 10 registros del Top
                if len(top_final) == 10:
                    break

            # Reconvertimos la lista de filas filtradas a un DataFrame para empaquetar
            if top_final:
                top_por_estado = pd.DataFrame(top_final)
            else:
                top_por_estado = pd.DataFrame(columns=["estado", "carrera", "alumnos", "indice_demanda"])

            # 6. SELECCIONAR LOS DATOS FINALES PARA EL DICT/JSON
            top_demanda = (
                top_por_estado[["estado", "carrera", "alumnos", "indice_demanda"]]
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