import os
from pathlib import Path

# Base Paths (Relative to the script execution or absolute)
# Asumiendo que el script corre desde 'recomendacion/' y los datos estan en 'AP/'
BASE_DIR = Path(r"c:\Users\sacorreac\OneDrive - Sector Agro\AP")

# Input Variables
SEMANA_R = "Semana37" # Default, can be overridden
ANIO_ACTUAL = "2025" # Explicitly setting for now as per files found

# Rutas de Archivos de Entrada (Mapeadas de los hallazgos)
RUTAS = {
    "eficiencia": BASE_DIR / "6. FERTILIZACION TV/csv a cargar/Tabla_eficiencia.csv",
    "eficiencia_variedades": BASE_DIR / "6. FERTILIZACION TV/csv a cargar/Eficiencia_variedades.csv", # Assuming existence based on standard
    "recomendacion": BASE_DIR / "6. FERTILIZACION TV/csv a cargar/Recomendacion.xlsx",
    "compost": BASE_DIR / "6. FERTILIZACION TV/csv a cargar/Compost.xlsx",
    "vinaza": BASE_DIR / "6. FERTILIZACION TV/csv a cargar/Vinaza.xlsx",
    "da_ref": BASE_DIR / "6. FERTILIZACION TV/csv a cargar/DA.csv",
    "inventario_muestreo": BASE_DIR / "6. FERTILIZACION TV/Datos_muestreo_optimizado/Inventario area muestreo optimizado.xlsx",
    "puntos_muestreo_opt": BASE_DIR / "6. FERTILIZACION TV/Datos_muestreo_optimizado/Ptos_actual.shp",
    "puntos_muestreo_gen": BASE_DIR / "6. FERTILIZACION TV/Fertilizacion shp/suelos/Puntos de muestreo/As_Grilla_General_muestreo1.shp",
    "parametros_kriging": BASE_DIR / "6. FERTILIZACION TV/csv a cargar/Tabla_parametros_kriging.xlsx",
    "parametros_interpolacion": BASE_DIR / "6. FERTILIZACION TV/Datos_muestreo_optimizado/Tabla variables interpolacion_Analisis Lab_V2.xlsx",
    "shp_hacienda": BASE_DIR / "6. FERTILIZACION TV/Fertilizacion shp/Ultima cartografia/hda.shp",
    "shp_suerte_bound": BASE_DIR / "6. FERTILIZACION TV/Fertilizacion shp/Ultima cartografia/ste.shp",
    "mapas_productividad": BASE_DIR / "9. MAPAS DE PRODUCTIVIDAD",
}

# Database Config
DB_CONFIG = {
    "server": "AGROIPSAVDB01\\PROD",
    "database": "SIAGRI_AG",
    "uid": "sg_interf",
    "pwd": "PIFAC4598",
    "driver": "SQL Server Native Client 11.0"
}

# Interpolation Settings
INTERPOLATION = {
    "idw_power": 0.5,
    "nmax": 20
}

# Output Paths
OUTPUT_DIR = BASE_DIR / "6. FERTILIZACION TV/Salidas"

def get_output_path(hacienda, semana=SEMANA_R):
    path = OUTPUT_DIR / hacienda / ANIO_ACTUAL / semana
    return path
