import pandas as pd
import re

# =========================
# 1. Cargar base desde R
# =========================
ruta = r"C:\Users\sacorreac\OneDrive - Sector Agro\AP\7. INFORMES FERTILIZACION TV\cargar\BD_Informes_Fertilizacion.xlsx"
df = pd.read_excel(ruta, dtype={"Hacienda": str})

# =========================
# 2. Identificar columnas métricas
# =========================
columnas_metricas = [
    c for c in df.columns
    if c.startswith("Area ") or c.startswith("Porcentaje ")
]


# =========================
# 3. Pasar de wide → long
# =========================
df_long = df.melt(
    id_vars=[c for c in df.columns if c not in columnas_metricas],
    value_vars=columnas_metricas,
    var_name="Indicador",
    value_name="Valor"
)

# =========================
# 4. Funciones auxiliares
# =========================
def extraer_motor(texto):
    if "Motor 1" in texto:
        return "Motor 1"
    if "Motor 2" in texto:
        return "Motor 2"
    if "Motor 3" in texto:
        return "Motor 3"
    if "Motores" in texto:
        return "Total"
    return "No aplica"

def extraer_tipo(texto):
    if "Velocidad" in texto:
        return "Velocidad"
    return "Aplicación"

def extraer_metrica(texto):
    if texto.startswith("Porcentaje"):
        return "Porcentaje"
    return "Área"

def extraer_clasificacion(texto):
    texto = texto.lower()
    if "sobre" in texto:
        return "Sobre"
    if "sub" in texto:
        return "Sub"
    if "optima" in texto:
        return "Óptima"
    if "alta" in texto:
        return "Alta"
    if "baja" in texto:
        return "Baja"
    return "Sin clasificar"

# =========================
# 5. Crear dimensiones
# =========================
df_long["Motor"] = df_long["Indicador"].apply(extraer_motor)
df_long["Tipo"] = df_long["Indicador"].apply(extraer_tipo)
df_long["Métrica"] = df_long["Indicador"].apply(extraer_metrica)
df_long["Clasificación"] = df_long["Indicador"].apply(extraer_clasificacion)

# =========================
# 6. Limpieza final
# =========================
df_long = df_long.drop(columns=["Indicador"])

# Eliminar filas sin valor o en cero si quieres
df_long = df_long.dropna(subset=["Valor"])
df_long = df_long[df_long["Valor"] > 0]

# =========================
# 7. Reordenar columnas
# =========================
orden = [
    "Zona", "Hacienda", "Suerte", "Hac_ste",
    "Fecha_Labor", "Año", "Mes",
    "Motor", "Tipo", "Clasificación", "Métrica", "Valor",
    "Area_ste", "Area_aplicada"
]

df_long = df_long[[c for c in orden if c in df_long.columns]]
# =========================
# 8. Guardar salida dinámica
# =========================

salida = r"C:\Users\sacorreac\OneDrive - Sector Agro\AP\scripts\4_antigravity\BD_Informes_Fertilizacion_modelo.xlsx"
df_long.to_excel(salida, index=False)

print("✅ Base normalizada creada correctamente")
print(f"📁 Archivo: {salida}")

#=========================
#8. CARGAR RECOMENDACIONES
#=========================

# Ruta recomendaciones
ruta_rec = r"C:\Users\sacorreac\OneDrive - Sector Agro\AP\6. FERTILIZACION TV\BD Compilado Recomendaciones.xlsx"

df_rec = pd.read_excel(ruta_rec, dtype={"Hacienda": str, "Suerte": str})
print(df_rec.dtypes)
df_rec.describe()
# Crear ID en ambas tablas
df_long["ID"] = df_long["Hacienda"] + df_long["Suerte"]
df_rec["ID"] = df_rec["Hacienda"] + df_rec["Suerte"]

# Convertir fechas
df_long["Fecha_Labor"] = pd.to_datetime(df_long["Fecha_Labor"])
df_rec["Fecha"] = pd.to_datetime(df_rec["Fecha"])


#=========================
#9. CONSOLIDAR FRACCIONES
#=========================

df_rec_group = (
    df_rec
    .groupby(["ID", "Fecha"], as_index=False)
    .agg({
        "Zona": "first",
        "Hacienda": "first",
        "Suerte": "first",
        "Área a aplicar": "first",
        "TCH Esperado": "first",
        "Variedad": "first",
        "Kg/Ha": "sum",
        "Unidades": "sum",
        "Kg totales": "sum",
        "Bultos": "sum",
        "Unidades_refuerzo": "sum"
    })
)

#=========================
#10. MERGE TEMPORAL
#=========================


# Orden estricto requerido por merge_asof
# Verificar orden
df_long = df_long.sort_values("Fecha_Labor").reset_index(drop=True)
df_rec_group = df_rec_group.sort_values("Fecha").reset_index(drop=True)
# Merge inteligente
df_final = pd.merge_asof(
    df_long,
    df_rec_group,
    left_on="Fecha_Labor",
    right_on="Fecha",
    by="ID",
    direction="backward"  # trae la recomendación anterior más cercana
)

# ======================================
# LIMPIAR COLUMNAS DESPUÉS DEL MERGE
# ======================================

# Eliminar columnas duplicadas de recomendación que no necesitas
columnas_conservar = [
    # Columnas originales calidad
    "Zona_x", "Hacienda_x", "Suerte_x", "Hac_ste",
    "Fecha_Labor", "Año", "Mes",
    "Motor", "Tipo", "Clasificación", "Métrica",
    "Valor", "Area_ste", "Area_aplicada",

    # Columnas recomendación importantes
    "Fecha",                 # fecha recomendación
    "Área a aplicar",
    "TCH Esperado",
    "Variedad",
    "Kg/Ha",
    "Unidades",
    "Kg totales"
]

df_final = df_final[[c for c in columnas_conservar if c in df_final.columns]]

df_final = df_final.rename(columns={
    "Zona_x": "Zona",
    "Hacienda_x": "Hacienda",
    "Suerte_x": "Suerte",
    "Fecha": "Fecha_Recomendacion"
})


salida = r"C:\Users\sacorreac\OneDrive - Sector Agro\AP\scripts\4_antigravity\BD_Informes_Fertilizacion_con_recomendacion.xlsx"

df_final.to_excel(salida, index=False)

print("✅ Base normalizada + recomendación creada correctamente")
print(f"📁 Archivo: {salida}")
