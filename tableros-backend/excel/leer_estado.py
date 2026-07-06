import traceback
import numpy as np
import pandas as pd
from pathlib import Path

# =====================================================
# 🧼 LIMPIEZA TOTAL PARA EL RETORNO JSON (TU MÉTODO)
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
# 📁 CONFIGURACIÓN DE RUTAS (TU MAQUETA EXACTA)
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parent
EXCEL_DIR = BACKEND_DIR / "excel"
CSV_ALUMNOS = EXCEL_DIR / "20260602-alumno.csv"
CSV_PLANTELES = EXCEL_DIR / "20260602-planteles.csv"
CATALOGO_ENTIDADES = EXCEL_DIR / "Catalogo_entidades.csv"
CSV_CARRERAS = EXCEL_DIR / "20260602-carreras.csv"

# =====================================================
# 📊 AUXILIAR: LIMPIEZA EXTREMA DE ID/CÓDIGO (TU MÉTODO)
# =====================================================
def normalizar_codigo_estado(val):
    if pd.isna(val): return ""
    s = str(val).strip().split('.')[0]
    return s.lstrip('0') if s.lstrip('0') != "" else "0"

def corregir_caracteres_excel(texto):
    if pd.isna(texto): return ""
    return str(texto).strip().replace("MŽxico", "México")

# =====================================================
# 🟢 CATÁLOGO DE LA BARRA VERDE (TEXTO LIMPIO SIN ADM)
# =====================================================
def obtener_estados():
    try:
        if not CATALOGO_ENTIDADES.exists(): return []
        df_ent = pd.read_csv(CATALOGO_ENTIDADES, sep=";", encoding="latin1", low_memory=False)
        df_ent.columns = df_ent.columns.str.strip().str.lower()
        
        palabras_excluidas = ["servicio exterior", "oficinas nacionales", "of. nacionales", "of.nacionales", "institucionales"]
        resultado_nombres = []
        for _, row in df_ent.iterrows():
            nombre_entidad = corregir_caracteres_excel(row["nombreentidad"])
            if any(p in nombre_entidad.lower() for p in palabras_excluidas):
                continue
            if nombre_entidad and not nombre_entidad.isdigit():
                resultado_nombres.append(nombre_entidad)
                
        return limpiar_nan(sorted(list(set(resultado_nombres))))
    except Exception:
        return []

# =====================================================
# 📊 AUXILIAR: RESOLVER TRADUCCIÓN ID <-> TEXTO DEL ESTADO
# =====================================================
def obtener_mapeo_entidades():
    txt_a_id = {}
    id_a_txt = {}
    try:
        if CATALOGO_ENTIDADES.exists():
            df_ent = pd.read_csv(CATALOGO_ENTIDADES, sep=";", encoding="latin1", low_memory=False)
            df_ent.columns = df_ent.columns.str.strip().str.lower()
            for _, row in df_ent.iterrows():
                cve = normalizar_codigo_estado(row["cveentidad"])
                nom = corregir_caracteres_excel(row["nombreentidad"])
                if cve and nom:
                    txt_a_id[nom.upper().strip()] = cve
                    id_a_txt[cve] = nom
    except Exception:
        pass
    return txt_a_id, id_a_txt

# =====================================================
# 📊 MÉTRICAS CONSOLIDADAS POR ESTADO (TU ESTILO INDIVIDUAL)
# =====================================================
def calcular_metricas_estado(df, nombre_o_id_estado):
    try:
        txt_a_id, id_a_txt = obtener_mapeo_entidades()
        target_txt = str(nombre_o_id_estado).strip()
        
        target_id = txt_a_id.get(target_txt.upper(), normalizar_codigo_estado(target_txt))
        nombre_oficial = id_a_txt.get(target_id, target_txt)
        df.columns = df.columns.str.strip().str.lower()
        
        col_ent = next((c for c in df.columns if "ent" in c or "cveent" in c), df.columns[0])
        df["cve_col_clean"] = df[col_ent].apply(normalizar_codigo_estado)
        
        df_filtered = df[df["cve_col_clean"] == target_id].copy()
        total_matricula = int(df_filtered["matricula"].nunique()) if "matricula" in df_filtered.columns else len(df_filtered)
        
        if total_matricula == 0:
            return {"estado": nombre_oficial, "matricula": 0, "promedio": 0.0, "regulares": 0, "irregulares": 0, "regularidad": 0.0}
            
        col_calif = "promg" if "promg" in df_filtered.columns else ("cspromgral" if "cspromgral" in df_filtered.columns else "califfinal")
        
        if col_calif in df_filtered.columns:
            df_filtered["calif_num"] = pd.to_numeric(df_filtered[col_calif], errors="coerce")
            promedio_gen = round(df_filtered["calif_num"].mean(), 2) if df_filtered["calif_num"].notna().any() else 0.0
            regulares = int(df_filtered[df_filtered["calif_num"] >= 8.0]["matricula"].nunique()) if "matricula" in df_filtered.columns else int((df_filtered["calif_num"] >= 8.0).sum())
        else:
            promedio_gen = 0.0
            regulares = 0
            
        irregulares = total_matricula - regulares
        
        return {
            "estado": nombre_oficial,
            "matricula": total_matricula,
            "promedio": promedio_gen,
            "regulares": regulares,
            "irregulares": irregulares,
            "regularidad": round((regulares / total_matricula) * 100, 2) if total_matricula > 0 else 0.0
        }
    except Exception:
        return {"estado": str(nombre_o_id_estado), "matricula": 0, "promedio": 0.0, "regulares": 0, "irregulares": 0, "regularidad": 0.0}

# =====================================================
# 🔄 ENDPOINTS CONSUMIDOS POR LAS GRÁFICAS DEL FRONT
# =====================================================
def obtener_regularidad_estados(estados_solicitados: list):
    try:
        if not CSV_ALUMNOS.exists(): return []
        df = pd.read_csv(CSV_ALUMNOS, low_memory=False)
        
        resultado = []
        for edo in estados_solicitados:
            met = calcular_metricas_estado(df, edo)
            if met["matricula"] > 0:
                resultado.append({
                    "estado": met["estado"],
                    "regular": met["regularidad"], 
                    "irregular": round(100 - met["regularidad"], 2)
                })
        return limpiar_nan(resultado)
    except Exception: return []

def obtener_nivel_desempeno_estados(estados_solicitados: list):
    try:
        if not CSV_ALUMNOS.exists(): return []
        df = pd.read_csv(CSV_ALUMNOS, low_memory=False)
        df.columns = df.columns.str.strip().str.lower()
        
        txt_a_id, _ = obtener_mapeo_entidades()
        col_calif = "promg" if "promg" in df.columns else "califfinal"
        
        resultado = []
        for edo in estados_solicitados:
            target_id = txt_a_id.get(str(edo).upper().strip(), normalizar_codigo_estado(edo))
            col_ent = next((c for c in df.columns if "ent" in c or "cveent" in c), df.columns[0])
            
            df_filtered = df[df[col_ent].apply(normalizar_codigo_estado) == target_id].copy()
            total = len(df_filtered)
            if total == 0: continue
            
            df_filtered["calif_num"] = pd.to_numeric(df_filtered[col_calif], errors="coerce")
            bins = [0, 6.99, 7.99, 8.99, 10]
            labels = ["bajo", "medio", "alto", "excelente"]
            df_filtered["nivel"] = pd.cut(df_filtered["calif_num"], bins=bins, labels=labels, include_lowest=True)
            
            conteo = df_filtered["nivel"].value_counts().reindex(labels, fill_value=0)
            resultado.append({
                "estado": str(edo).strip(),
                "bajo": round((conteo["bajo"] * 100) / total, 2),
                "medio": round((conteo["medio"] * 100) / total, 2),
                "alto": round((conteo["alto"] * 100) / total, 2),
                "excelente": round((conteo["excelente"] * 100) / total, 2),
            })
        return limpiar_nan(resultado)
    except Exception: return []

def obtener_top_planteles(estados_solicitados: list):
    try:
        if not CSV_ALUMNOS.exists() or not CSV_PLANTELES.exists(): return []
        df_alu = pd.read_csv(CSV_ALUMNOS, low_memory=False)
        df_pla = pd.read_csv(CSV_PLANTELES, low_memory=False)
        
        df_alu.columns = df_alu.columns.str.strip().str.lower()
        df_pla.columns = df_pla.columns.str.strip().str.lower()
        
        txt_a_id, _ = obtener_mapeo_entidades()
        col_ent = next((c for c in df_alu.columns if "ent" in c or "cveent" in c), df_alu.columns[0])
        col_calif = "promg" if "promg" in df_alu.columns else "califfinal"
        
        df_alu["calif_num"] = pd.to_numeric(df_alu[col_calif], errors="coerce")
        df_alu["cveunidadmin"] = df_alu["cveunidadmin"].astype(str).str.strip()
        df_pla["cveunidadmin"] = df_pla["cveunidadmin"].astype(str).str.strip()
        
        df_pla_clean = df_pla.rename(columns={"descripcion": "nombre_plantel"})
        df = df_alu.merge(df_pla_clean[["cveunidadmin", "nombre_plantel"]], on="cveunidadmin", how="left")
        
        resultado_final = []
        for edo in estados_solicitados:
            target_id = txt_a_id.get(str(edo).upper().strip(), normalizar_codigo_estado(edo))
            df_edo = df[df[col_ent].apply(normalizar_codigo_estado) == target_id].dropna(subset=["calif_num", "nombre_plantel"])
            if df_edo.empty: continue
            
            grouped = df_edo.groupby("nombre_plantel")["calif_num"].mean().reset_index()
            grouped = grouped.sort_values(by="calif_num", ascending=False).head(3)
            
            for _, r in grouped.iterrows():
                resultado_final.append({
                    "nombreentidad": str(edo).strip(),
                    "nombre_plantel": str(r["nombre_plantel"]),
                    "promg": round(r["calif_num"], 2)
                })
        return limpiar_nan(resultado_final)
    except Exception: return []