import pandas as pd
import geopandas as gpd
import pyodbc
import logging
from pathlib import Path
import config

logger = logging.getLogger(__name__)

def get_sql_connection():
    """
    Establishes a connection to the SQL Server database.
    Retries or fails gracefully if connection fails.
    """
    conn_str = (
        f"DRIVER={{{config.DB_CONFIG['driver']}}};"
        f"SERVER={config.DB_CONFIG['server']};"
        f"DATABASE={config.DB_CONFIG['database']};"
        f"UID={config.DB_CONFIG['uid']};"
        f"PWD={config.DB_CONFIG['pwd']}"
    )
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as ex:
        logger.error(f"Error connecting to SQL Server: {ex}")
        raise

def get_field_area(hacienda, suerte):
    """
    Fetches the AREA_P for a specific Hacienda and Suerte from the database.
    """
    query = f"SELECT AREA_P AREA FROM TALHAO WITH(NOLOCK) WHERE FAZ = '{hacienda}' AND TAL = '{suerte}'"
    try:
        conn = get_sql_connection()
        data = pd.read_sql(query, conn)
        conn.close()
        if not data.empty:
            return data.iloc[0]['AREA']
        else:
            logger.warning(f"No area found for Hda: {hacienda}, Ste: {suerte}")
            return 0.0
    except Exception as e:
        logger.error(f"Failed to fetch field area: {e}")
        return 0.0

def load_shapefile(path):
    """
    Loads a shapefile using Geopandas.
    """
    try:
        if not Path(path).exists():
            raise FileNotFoundError(f"Shapefile not found: {path}")
        return gpd.read_file(path)
    except Exception as e:
        logger.error(f"Error loading shapefile {path}: {e}")
        raise

def load_excel(path, sheet_name=0, **kwargs):
    """
    Loads an Excel file using Pandas.
    """
    try:
        if not Path(path).exists():
            raise FileNotFoundError(f"Excel file not found: {path}")
        return pd.read_excel(path, sheet_name=sheet_name, **kwargs)
    except Exception as e:
        logger.error(f"Error loading excel {path}: {e}")
        raise

def get_compost_dose(hacienda, suerte, df_compost):
    """Matches R's compost() function."""
    if df_compost.empty:
        return 0
    # R: subset(df_compost, NOME_ACTIVIDAD == "TRANSPORTE DEL COMPOST")
    # And then subset by HACIENDA, SUERTE
    # Note: hacienda/suerte should be normalized or matched as they appear in the file
    mask = (df_compost['HACIENDA'].astype(str) == str(hacienda)) & (df_compost['SUERTE'].astype(str) == str(suerte))
    if 'NOME_ACTIVIDAD' in df_compost.columns:
        mask &= (df_compost['NOME_ACTIVIDAD'] == "TRANSPORTE DEL COMPOST")
    
    subset = df_compost[mask]
    if subset.empty:
        return 0
    return float(subset.iloc[0]['Dosis'])

def get_vinaza_dose(hacienda, suerte, df_vinaza):
    """Matches R's vinaza() function."""
    if df_vinaza.empty:
        return 0
    # R: subset(df_vinaza, NOME_PRODUCTO == "VINAZA DESPACHADA")
    mask = (df_vinaza['HACIENDA'].astype(str) == str(hacienda)) & (df_vinaza['SUERTE'].astype(str) == str(suerte))
    if 'NOME_PRODUCTO' in df_vinaza.columns:
        mask &= (df_vinaza['NOME_PRODUCTO'] == "VINAZA DESPACHADA")
        
    subset = df_vinaza[mask]
    if subset.empty:
        return 0
    # R: a$DOSIS[1] / 1000
    return float(subset.iloc[0]['DOSIS']) / 1000.0

def load_csv(path, sep=';', encoding='latin-1'):
    """
    Loads a CSV file.
    """
    try:
        if not Path(path).exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        return pd.read_csv(path, sep=sep, encoding=encoding)
    except Exception as e:
        logger.error(f"Error loading CSV {path}: {e}")
        raise
