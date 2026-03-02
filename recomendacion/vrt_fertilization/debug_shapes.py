import geopandas as gpd
import pandas as pd
import config

print("Loading Shapefiles...")
gdf_hda = gpd.read_file(config.RUTAS['shp_hacienda'])
gdf_ste = gpd.read_file(config.RUTAS['shp_suerte_bound'])

print("\n--- Hacienda Shapefile Columns ---")
print(gdf_hda.columns)
print("\n--- Hacienda Sample Data ---")
print(gdf_hda.head())

print("\n--- Suerte Shapefile Columns ---")
print(gdf_ste.columns)
print("\n--- Suerte Sample Data ---")
print(gdf_ste.head())

print("\n--- Recommendation Excel Sample ---")
df_recom = pd.read_excel(config.RUTAS['recomendacion'])
print(df_recom[['Hacienda', 'Suerte']].head())
print("\n--- Types in Recommendation ---")
print(df_recom[['Hacienda', 'Suerte']].dtypes)
