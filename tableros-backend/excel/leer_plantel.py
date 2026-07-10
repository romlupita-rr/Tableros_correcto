import traceback
import numpy as np
import pandas as pd
from pathlib import Path

# =====================================================
# 🧼 LIMPIEZA TOTAL PARA EL RETORNO JSON
# =====================================================
def limpiar_nan(data):
    if isinstance(data, list): return [limpiar_nan(i) for i in data]
    if isinstance(data, dict): return {k: limpiar_nan(v) for k, v in data.items()}
    try:
        if pd.isna(data): return None
    except Exception: pass
    if isinstance(data, (np.integer, np.floating)): return data.item()
    return data


# =====================================================
# 📁 CONFIGURACIÓN DE RUTAS
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parent
EXCEL_DIR = BACKEND_DIR / "excel"

CSV_ALUMNOS = EXCEL_DIR / "20260602-alumno.csv"
CSV_PLANTELES = EXCEL_DIR / "20260602-planteles.csv"
CATALOGO_ENTIDADES = EXCEL_DIR / "Catalogo_entidades.csv"
CSV_MODULOS = EXCEL_DIR / "20260602-alumnomodulo .csv"

if not CSV_MODULOS.exists():
    CSV_MODULOS = EXCEL_DIR / "20260602-alumnomodulo.csv"

# Se declara de forma global fija para asegurar su acceso en todo el script
CSV_CARRERAS = EXCEL_DIR / "20260602-carreras.csv"


# =====================================================
# 📡 PERIODOS ESCOLARES
# =====================================================
def obtener_periodos_escolares():
    try:
        if not CSV_MODULOS.exists(): return []
        df = pd.read_csv(CSV_MODULOS, encoding="latin1", low_memory=True)
        df.columns = df.columns.str.strip().str.lower()
        return df["periodoescolar"].dropna().astype(str).str.strip().unique().tolist()
    except Exception: return []


# =====================================================
# 🟢 CATÁLOGO DE LA BARRA VERDE (CON FILTRO ADM)
# =====================================================
def obtener_catalogo_completo():
    try:
        if not CATALOGO_ENTIDADES.exists() or not CSV_PLANTELES.exists(): return []
        
        df_ent = pd.read_csv(CATALOGO_ENTIDADES, sep=";", encoding="latin1", low_memory=False)
        df_ent.columns = df_ent.columns.str.strip().str.lower()
        
        df_pla = pd.read_csv(CSV_PLANTELES, low_memory=False)
        df_pla.columns = df_pla.columns.str.strip().str.lower()

        palabras_excluidas = ["servicio exterior", "oficinas nacionales", "of. nacionales", "of.nacionales"]

        planteles_por_entidad = {}
        for _, row in df_pla.iterrows():
            try:
                descripcion_plantel = str(row["descripcion"]).strip()
                if any(p in descripcion_plantel.lower() for p in palabras_excluidas):
                    continue

                cve_ent = str(row["cveentidad"]).strip()
                plantel_info = {
                    "cveunidadmin": str(row["cveunidadmin"]).strip(),
                    "descripcion": descripcion_plantel
                }
                if cve_ent not in planteles_por_entidad: planteles_por_entidad[cve_ent] = []
                planteles_por_entidad[cve_ent].append(plantel_info)
            except Exception: continue

        resultado = []
        for _, row in df_ent.iterrows():
            try:
                nombre_entidad = str(row["nombreentidad"]).strip().replace("MŽxico", "México")
                if any(p in nombre_entidad.lower() for p in palabras_excluidas):
                    continue

                cve_ent = str(row["cveentidad"]).strip()
                resultado.append({
                    "cveentidad": cve_ent,
                    "nombreentidad": nombre_entidad,
                    "planteles": planteles_por_entidad.get(cve_ent, [])
                })
            except Exception: continue
        return resultado
    except Exception: return []


# =====================================================
# 📊 AUXILIAR: LIMPIEZA EXTREMA DE ID/CÓDIGO
# =====================================================
def normalizar_codigo_plantel(val):
    s = str(val).strip().split('.')[0]
    return s.lstrip('0')


# =====================================================
# 📊 CÁLCULO DE MÉTRICAS INDIVIDUALES (MODIFICADO PARA CARRERAS)
# =====================================================
def calcular_metricas_plantel(df, cve_plantel):
    try:
        valor_buscado = str(cve_plantel).strip()
        nombre_alternativo = ""
        
        if CSV_PLANTELES.exists():
            try:
                df_pla_aux = pd.read_csv(CSV_PLANTELES, low_memory=False)
                df_pla_aux.columns = df_pla_aux.columns.str.strip().str.lower()
                
                df_pla_aux["cve_normalizada"] = df_pla_aux["cveunidadmin"].apply(normalizar_codigo_plantel)
                id_busqueda_limpia = normalizar_codigo_plantel(valor_buscado)
                
                match_id = df_pla_aux[df_pla_aux["cve_normalizada"] == id_busqueda_limpia]
                if not match_id.empty:
                    nombre_alternativo = str(match_id.iloc[0]["descripcion"]).strip().lower()
                    valor_buscado = str(match_id.iloc[0]["cveunidadmin"]).strip()
                else:
                    termino_limpio = valor_buscado.lower().replace(" ", "")
                    df_pla_aux['desc_limpia'] = df_pla_aux["descripcion"].astype(str).str.lower().str.replace(" ", "")
                    match_txt = df_pla_aux[df_pla_aux['desc_limpia'].str.contains(termino_limpio, na=False)]
                    if not match_txt.empty:
                        valor_buscado = str(match_txt.iloc[0]["cveunidadmin"]).strip()
                        nombre_alternativo = str(match_txt.iloc[0]["descripcion"]).strip().lower()
            except Exception:
                pass

        df.columns = df.columns.str.strip().str.lower()
        df_filtered = pd.DataFrame()

        id_final_target = normalizar_codigo_plantel(valor_buscado)
        
        for col in df.columns:
            if "unidad" in col or "plantel" in col or "cve" in col:
                try:
                    df["cve_col_clean"] = df[col].apply(normalizar_codigo_plantel)
                    subset = df[df["cve_col_clean"] == id_final_target]
                    if not subset.empty:
                        df_filtered = subset
                        break
                except Exception:
                    continue

        if df_filtered.empty and nombre_alternativo:
            palabras = [p for p in nombre_alternativo.split() if len(p) > 3 and p not in ["escuela", "instituto", "pruebas", "de", "del"]]
            palabra_clave = palabras[0] if palabras else nombre_alternativo
            
            for col in df.columns:
                if "desc" in col or "nombre" in col or "plantel" in col:
                    try:
                        subset = df[df[col].astype(str).str.lower().str.contains(palabra_clave, na=False)]
                        if not subset.empty:
                            df_filtered = subset
                            break
                    except Exception:
                        continue

        total_matricula = int(df_filtered["matricula"].nunique()) if "matricula" in df_filtered.columns else len(df_filtered)
        
        if total_matricula == 0:
            return {"matricula": 0, "promedio": 0.0, "regulares": 0, "regulares_pct": 0.0, "irregulares": 0, "irregulares_pct": 0.0, "carreras": []}

        col_calif = "promg" if "promg" in df_filtered.columns else ("cspromgral" if "cspromgral" in df_filtered.columns else "califfinal")
        
        if col_calif in df_filtered.columns:
            df_filtered["calif_num"] = pd.to_numeric(df_filtered[col_calif], errors="coerce")
            promedio_gen = round(df_filtered["calif_num"].mean(), 2) if df_filtered["calif_num"].notna().any() else 0.0
            regulares = int(df_filtered[df_filtered["calif_num"] >= 7.0]["matricula"].nunique()) if "matricula" in df_filtered.columns else int((df_filtered["calif_num"] >= 7.0).sum())
        else:
            promedio_gen = 0.0
            regulares = 0

        irregulares = total_matricula - regulares

        # =====================================================
        # 📊 NUEVA EXTRACCIÓN: PROMEDIO POR CARRERA PARA LA GRÁFICA
        # =====================================================
        carreras_list = []
        if "cveplanestudio" in df_filtered.columns and col_calif in df_filtered.columns:
            try:
                mapa_exacto = {}
                mapa_raiz = {}
                if CSV_CARRERAS.exists():
                    df_cat = pd.read_csv(CSV_CARRERAS, skiprows=1, names=["modelo", "cve", "descripcion", "descorta"], encoding="latin1")
                    for _, row in df_cat.iterrows():
                        cve_orig = str(row["cve"]).upper().strip()
                        if cve_orig and cve_orig != "NAN":
                            mapa_exacto[cve_orig] = str(row["descripcion"]).strip()
                            if len(cve_orig) >= 4:
                                mapa_raiz[cve_orig[:4]] = str(row["descripcion"]).strip()

                df_car = df_filtered.copy()
                df_car["cveplanestudio"] = df_car["cveplanestudio"].astype(str).str.upper().str.strip()
                
                df_res = (
                    df_car.dropna(subset=["calif_num", "cveplanestudio"])
                    .groupby("cveplanestudio")
                    .agg(promedio=("calif_num", "mean"))
                    .reset_index()
                )
                df_res["promedio"] = df_res["promedio"].round(1) # Un decimal como en tu imagen (Ej: 8.9)

                def obtener_nombre_carrera(cve):
                    cve_clean = str(cve).upper().strip()
                    if cve_clean in mapa_exacto: return mapa_exacto[cve_clean]
                    if len(cve_clean) >= 4 and cve_clean[:4] in mapa_raiz: return mapa_raiz[cve_clean[:4]]
                    return cve

                def limpiar_texto_carrera(texto):
                    t = str(texto)
                    replacements = {
                        "TÃ©cnico": "Técnico", "InformÃ¡tica": "Informática",
                        "EnfermerÃ­a": "Enfermería", "MecatrÃ³nica": "Mecatrónica",
                        "AdministraciÃ³n": "Administración", "Contabilidad": "Contabilidad"
                    }
                    for k, v in replacements.items(): t = t.replace(k, v)
                    # Quita el prefijo institucional largo para que se lea limpio como en tu diseño
                    t = t.replace("Profesional Técnico-Bachiller en ", "").replace("Profesional Técnico en ", "")
                    t = t.replace("Profesional TÃ©cnico-Bachiller en ", "")
                    return t.strip()

                df_res["carrera"] = df_res["cveplanestudio"].apply(obtener_nombre_carrera).apply(limpiar_texto_carrera)
                carreras_list = df_res.sort_values("promedio", ascending=False)[["carrera", "promedio"]].to_dict("records")
            except Exception:
                carreras_list = []
        
        return {
            "matricula": total_matricula,
            "promedio": promedio_gen,
            "regulares": regulares,
            "regulares_pct": round((regulares / total_matricula) * 100, 2) if total_matricula > 0 else 0.0,
            "irregulares": irregulares,
            "irregulares_pct": round((irregulares / total_matricula) * 100, 2) if total_matricula > 0 else 0.0,
            "carreras": carreras_list # <--- Inyectado con éxito
        }
    except Exception:
        return {"matricula": 0, "promedio": 0.0, "regulares": 0, "regulares_pct": 0.0, "irregulares": 0, "irregulares_pct": 0.0, "carreras": []}


# =====================================================
# 🔄 COMPARADOR ENTRE DOS PLANTELES
# =====================================================
def obtener_comparacion_planteles(cve_p1, cve_p2, periodo):
    try:
        if not CSV_ALUMNOS.exists(): return {}
        df = pd.read_csv(CSV_ALUMNOS, low_memory=False)
        df.columns = df.columns.str.strip().str.lower()
        if periodo and "periodoescolar" in df.columns:
            df = df[df["periodoescolar"].astype(str).str.strip() == str(periodo).strip()]
        
        # Al ejecutar esto, "p1" y "p2" ya llevarán su llave "carreras" con el arreglo listo
        return limpiar_nan({"p1": calcular_metricas_plantel(df, cve_p1), "p2": calcular_metricas_plantel(df, cve_p2)})
    except Exception: return {}


# =====================================================
# 📦 INTERFAZ GENERAL REQUERIDA POR EL DASHBOARD
# =====================================================
def obtener_metricas_nacionales():
    return limpiar_nan({
        "periodos_escolares": obtener_periodos_escolares(),
        "catalogo_estructura": obtener_catalogo_completo()
    })