import pandas as pd
import geopandas as gpd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_directory(path):
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {path}")
    return path

def save_excel_report(dataframe, filepath, sheet_name="Hoja1"):
    """
    Saves a DataFrame to an Excel file.
    """
    try:
        ensure_directory(filepath.parent)
        dataframe.to_excel(filepath, index=False, sheet_name=sheet_name)
        logger.info(f"Saved Excel report to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save Excel {filepath}: {e}")
        raise

def save_shapefile(gdf, filepath, layer_name=None):
    """
    Saves a GeoDataFrame to a Shapefile.
    """
    try:
        ensure_directory(filepath.parent)
        # Verify CRS, set to WGS84 or requested
        if gdf.crs is None:
             logger.warning("GeoDataFrame has no CRS. Setting to generic but check this.")
        
        gdf.to_file(filepath, driver='ESRI Shapefile')
        logger.info(f"Saved Shapefile to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save Shapefile {filepath}: {e}")
        raise
