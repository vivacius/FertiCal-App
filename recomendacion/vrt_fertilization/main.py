import pandas as pd
import geopandas as gpd
import numpy as np
import logging
import sys
from pathlib import Path
from tqdm import tqdm

try:
    from . import config
    from .src import data_loader, spatial, agronomy, optimization, reporting
except ImportError:
    # Fallback to absolute imports if run as script
    import config
    from src import data_loader, spatial, agronomy, optimization, reporting

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vrt_process.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MAIN")

def main():
    logger.info("Starting VRT Fertilization Process")
    
    # 1. Load Global Config & Tables
    try:
        logger.info(f"Loading efficiency table from {config.RUTAS['eficiencia']}")
        df_efficiency = data_loader.load_csv(config.RUTAS['eficiencia'], sep=';')
        
        logger.info(f"Loading recommendation order from {config.RUTAS['recomendacion']}")
        df_recom = data_loader.load_excel(config.RUTAS['recomendacion'], dtype={'Hacienda': str})
        if 'Hacienda' in df_recom.columns:
             df_recom['Hacienda'] = df_recom['Hacienda'].astype(str).str.zfill(6)
        
        logger.info(f"Loading variety efficiency from {config.RUTAS['eficiencia_variedades']}")
        df_eff_var = data_loader.load_csv(config.RUTAS['eficiencia_variedades'], sep=';')

        # Load Soil Data References & Supplements
        logger.info(f"Loading DA reference table from {config.RUTAS['da_ref']}")
        df_da_ref = data_loader.load_csv(config.RUTAS['da_ref'], sep=';')
        
        logger.info(f"Loading Sampling Inventory from {config.RUTAS['inventario_muestreo']}")
        df_inventario = data_loader.load_excel(config.RUTAS['inventario_muestreo'], sheet_name="final", dtype={'Cod': str})
        if 'Cod' in df_inventario.columns:
             df_inventario['Cod'] = df_inventario['Cod'].astype(str).str.zfill(6)

        logger.info("Loading Compost and Vinaza tables...")
        df_compost_master = data_loader.load_excel(config.RUTAS['compost'])
        df_vinaza_master = data_loader.load_excel(config.RUTAS['vinaza'])

    except Exception as e:
        logger.critical(f"Failed to load base tables/supplements: {e}")
        return

    agronomy_engine = agronomy.AgronomyLogic(df_efficiency)

    # 2. Load Global Shapefiles
    try:
        logger.info("Loading global shapefiles...")
        gdf_hda_global = data_loader.load_shapefile(config.RUTAS['shp_hacienda'])
        gdf_ste_global = data_loader.load_shapefile(config.RUTAS['shp_suerte_bound'])
    except Exception as e:
        logger.error(f"Failed to load global shapefiles: {e}")
        return

    # 3. Main Loop
    COMPLETO_RESULTS = []
    PORC_N_COMPOST = 0.8 # Hardcoded in R line 1337
    PORC_N_VINAZA = 0.2  # Hardcoded in R line 1338
    
    for idx, row in tqdm(df_recom.iterrows(), total=df_recom.shape[0], desc="Processing Suertes"):
        hacienda = str(row['Hacienda'])
        suerte = str(row['Suerte'])
        variedad = str(row.get('Variedad', 'Unknown'))
        target_area_ha = row.get('Area a aplicar', 0)
        tche_target = row.get('TCH Esperado', 0)
        
        logger.info(f"Processing Hacienda: {hacienda}, Suerte: {suerte}")
        
        try:
            # A. Filter Geometry
            def get_col(df, candidates):
                for c in df.columns:
                    if c.upper() in [k.upper() for k in candidates]:
                        return c
                return None
            
            hac_col = get_col(gdf_hda_global, ['Hac', 'Hacienda', 'FAZ'])
            ste_col = get_col(gdf_ste_global, ['Ste', 'Suerte', 'TAL'])
            hac_col_ste = get_col(gdf_ste_global, ['Hac', 'Hacienda', 'FAZ']) 
            
            if not hac_col or not ste_col:
                logger.error("Could not identify Hacienda/Suerte columns in shapefiles.")
                continue
            
            def normalize_hacienda(val):
                s = str(val).strip().split('.')[0] 
                if s.isdigit() and len(s) < 6:
                    return s.zfill(6)
                return s

            hac_target = normalize_hacienda(hacienda)
            ste_target = str(suerte).strip().split('.')[0]
            
            gdf_hda_normalized = gdf_hda_global.copy()
            gdf_hda_normalized[hac_col] = gdf_hda_normalized[hac_col].astype(str).str.strip()
            gdf_hda_curr = gdf_hda_normalized[gdf_hda_normalized[hac_col] == hac_target]
            if gdf_hda_curr.empty:
                gdf_hda_curr = gdf_hda_normalized[gdf_hda_normalized[hac_col] == str(hacienda)]
            
            gdf_ste_normalized = gdf_ste_global.copy()
            gdf_ste_normalized[hac_col_ste] = gdf_ste_normalized[hac_col_ste].astype(str).str.strip()
            gdf_ste_normalized[ste_col] = gdf_ste_normalized[ste_col].astype(str).str.strip()
            gdf_ste_curr = gdf_ste_normalized[
                (gdf_ste_normalized[hac_col_ste] == hac_target) & 
                (gdf_ste_normalized[ste_col] == ste_target)
            ]
            
            if gdf_ste_curr.empty:
                logger.warning(f"Geometry not found for {hacienda}-{suerte}")
                continue

            # B. Processing Inputs
            # 1. Productivity Map
            prod_path = config.RUTAS['mapas_productividad'] / hac_target / config.ANIO_ACTUAL / ste_target / f"{hac_target}{ste_target}.shp"
            if not prod_path.exists():
                found_map = False
                for year_fallback in ["2024", "2023"]:
                    prod_path_alt = config.RUTAS['mapas_productividad'] / hac_target / year_fallback / ste_target / f"{hac_target}{ste_target}.shp"
                    if prod_path_alt.exists():
                        prod_path = prod_path_alt
                        found_map = True
                        break
                if not found_map:
                    logger.warning(f"Productivity map not found for {hac_target}-{ste_target}")
                    continue
                
            gdf_prod_points = data_loader.load_shapefile(prod_path)
            
            # 2. Variety Factor (fa_v) - R line 787
            v_match = df_eff_var[df_eff_var['Variedad'] == variedad]
            fa_v = float(v_match.iloc[0]['Fa_variedad']) if not v_match.empty else 1.2
            
            # 3. Compost & Vinaza NC/NV - R lines 827-828
            comp_dose = data_loader.get_compost_dose(hacienda, suerte, df_compost_master)
            vin_dose = data_loader.get_vinaza_dose(hacienda, suerte, df_vinaza_master)
            nc = ((comp_dose * 1000.0) * (PORC_N_COMPOST / 100.0)) / 2.0
            nv = ((vin_dose * 1000.0) * (PORC_N_VINAZA / 100.0)) / 2.0

            # 4. Soil Points (pH, MO, DA)
            use_opt = False
            inv_row = df_inventario[df_inventario['Cod'] == hac_target] 
            if not inv_row.empty:
                pct_col = get_col(df_inventario, ['%', 'Porcentaje'])
                if pct_col and inv_row.iloc[0][pct_col] == 1:
                     use_opt = True
            
            soil_shp_path = config.RUTAS['puntos_muestreo_opt'] if use_opt else config.RUTAS['puntos_muestreo_gen']
            gdf_soil_points = None
            if soil_shp_path.exists():
                 try:
                    gdf_soil_points = data_loader.load_shapefile(soil_shp_path)
                    gdf_soil_points = gpd.clip(gdf_soil_points, gdf_hda_curr.unary_union)
                 except:
                     gdf_soil_points = None

            # --- Interpolation ---
            grid_suerte = spatial.create_grid(gdf_ste_curr, cell_size=20)
            target_coords = grid_suerte[['x', 'y']].values
            
            # 5. Yield Pred & Shift (TCHE) - R lines 766-770
            coords_prod = np.array(list(zip(gdf_prod_points.geometry.x, gdf_prod_points.geometry.y)))
            prod_col = get_col(gdf_prod_points, ['Prod_New', 'Prod', 'Yield'])
            values_prod = pd.to_numeric(gdf_prod_points[prod_col], errors='coerce').fillna(0).values
            z_prod = spatial.idw_interpolation(coords_prod, values_prod, target_coords, power=0.5)
            
            if tche_target > 0:
                current_mean = np.mean(z_prod)
                shift = float(tche_target) - current_mean
                z_prod = z_prod + shift
            
            grid_suerte['yield_pred'] = z_prod 
            
            # 6. Soil Properties Interpolation
            grid_suerte['ph'] = 7.5
            grid_suerte['mo'] = 2.0
            grid_suerte['da'] = 1.2
            
            if gdf_soil_points is not None and not gdf_soil_points.empty:
                coords_soil = np.array(list(zip(gdf_soil_points.geometry.x, gdf_soil_points.geometry.y)))
                tex_col = get_col(gdf_soil_points, ['tex', 'Texture', 'Textura'])
                if tex_col and 'DA' not in gdf_soil_points.columns:
                     da_map = dict(zip(df_da_ref['Textura'], df_da_ref['DA']))
                     gdf_soil_points['DA'] = gdf_soil_points[tex_col].map(da_map).fillna(1.2)
                
                for prop, default_val in [('ph', 7.5), ('mo', 2.0), ('DA', 1.2)]:
                     col = get_col(gdf_soil_points, [prop, prop.upper()])
                     if col:
                         vals = pd.to_numeric(gdf_soil_points[col], errors='coerce').fillna(default_val).values
                         grid_suerte[prop.lower()] = spatial.idw_interpolation(coords_soil, vals, target_coords, power=0.5)
                     else:
                         grid_suerte[prop.lower()] = default_val

            # C. Agronomy Decision
            grid_suerte = agronomy_engine.calculate_spatial_dose(
                grid_suerte, 
                variety_factor=fa_v,
                compost_n=nc,
                vinaza_n=nv
            )
            
            n_requirement_mean = grid_suerte['Dosis'].mean()
            selected_mix = agronomy_engine.select_fertilizer(
                ph_avg=grid_suerte['ph'].mean(), 
                available_fertilizers=["Urea", "SAM", "Nitro_Xtends", "Naxtrom", "Nitrax"],
                shape_dosis_mean=n_requirement_mean
            )
            
            # D. Output Table & Hopper Opt
            real_area = data_loader.get_field_area(hac_target, ste_target) or float(target_area_ha)
            df_res = agronomy_engine.calculate_dose_table(
                shape_mean_dose=n_requirement_mean,
                proportions=selected_mix,
                field_area=real_area,
                area_to_apply_ha=float(target_area_ha)
            )
            
            hoppers = optimization.distribute_hoppers(df_res)
            grid_suerte = optimization.apply_hopper_distribution_to_shape(grid_suerte, hoppers)
            gdf_grid_out = gpd.GeoDataFrame(grid_suerte, geometry=gpd.points_from_xy(grid_suerte.x, grid_suerte.y), crs=gdf_prod_points.crs)
            
            # E. FINAL ROW (R Format)
            f_row = pd.Series()
            f_row["Fecha"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            f_row["Hacienda"] = hacienda
            f_row["Suerte"] = suerte
            f_row["Area_Cartografia"] = float(target_area_ha)
            f_row["Area real"] = real_area
            f_row["Kg/ste-Real"] = df_res['Kg totales'].sum()
            f_row["Kg/Ha-Real"] = df_res['Kg/Ha'].sum()
            f_row["Bultos/ste-Real"] = df_res['Bultos'].sum()
            f_row["TOLVA 1"] = hoppers.get("TOLVA 1", 0)
            f_row["TOLVA 2"] = hoppers.get("TOLVA 2", 0)
            f_row["TOLVA 3"] = hoppers.get("TOLVA 3", 0)
            f_row["Mix"] = ", ".join(selected_mix.keys())
            COMPLETO_RESULTS.append(f_row.to_frame().T)

            # F. Save Files
            zona = str(row.get('Zona', 'Unknown')).strip()
            base_output = config.OUTPUT_DIR / zona / config.ANIO_ACTUAL / config.SEMANA_R
            (base_output / f"{config.SEMANA_R}_excel").mkdir(parents=True, exist_ok=True)
            (base_output / f"{hac_target}{ste_target}").mkdir(parents=True, exist_ok=True)
            
            reporting.save_excel_report(df_res, base_output / f"{config.SEMANA_R}_excel" / f"{hac_target}{ste_target}_recomendacion.xlsx")
            reporting.save_shapefile(gdf_grid_out, base_output / f"{hac_target}{ste_target}" / f"{hac_target}{ste_target}_U.shp")
            reporting.save_excel_report(f_row.to_frame().T, base_output / f"{config.SEMANA_R}_excel" / f"{hac_target}{ste_target}_U_tolvas.xlsx")

        except Exception as e:
            logger.error(f"Error processing {hacienda}-{suerte}: {e}", exc_info=True)
            continue

    # G. Final Report
    if COMPLETO_RESULTS:
        df_completo = pd.concat(COMPLETO_RESULTS, ignore_index=True)
        df_completo.to_excel(config.OUTPUT_DIR / "completo_recomendacion.xlsx", index=False)
        logger.info("Saved Consolidated Report.")

if __name__ == "__main__":
    main()
