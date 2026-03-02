import geopandas as gpd
import config

print("Loading Shapefiles...")
gdf_hda = gpd.read_file(config.RUTAS['shp_hacienda'])
print("\n--- Unique Hac Values in Shapefile ---")
print(gdf_hda['Hac'].unique()[:20])

print("\n--- Unique Ste Values in Shapefile ---")
gdf_ste = gpd.read_file(config.RUTAS['shp_suerte_bound'])
print(gdf_ste['Ste'].unique()[:20])
