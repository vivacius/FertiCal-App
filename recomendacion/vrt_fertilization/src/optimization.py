import pandas as pd
import numpy as np
import itertools
import logging

logger = logging.getLogger(__name__)

def distribute_hoppers(recommendation_table):
    """
    Optimizes the distribution of fertilizer into hoppers (Tolvas).
    Replicates 'Distrib_tolvas' from R.
    
    Args:
        recommendation_table (pd.DataFrame): Output from calculate_dose_table
        
    Returns:
        dict: {tolva_1: val, tolva_2: val, ...} or updated DataFrame
    """
    if recommendation_table.empty:
        return None
    
    num_products = len(recommendation_table)
    
    # Pre-defined percentage settings from R code (line 1043)
    vec = [0, 0.22, 0.25, 0.255, 0.265, 0.3, 0.35, 0.375, 0.4, 0.43, 0.45, 
           0.47, 0.49, 0.5, 0.55, 0.56, 0.57, 0.6, 0.625, 0.65, 0.7, 1.0]
    
    best_combo = None
    
    if num_products == 1:
        target_dose = recommendation_table.iloc[0]['Kg/Ha'] # Modified to match agronomy output
        # R logic legacy: 'Kg/Ha-Real' was likely an alias or calculation result.
        # We proceed with the calculated Kg/Ha.
        # Table cols in R: Unidades, Kg/Ha, Kg Totales, Bultos, Costo, Refuerzo.
        # Wait, R line 1042 says tabla[1,5]. In 1-index, that's Costo ($).
        # That seems wrong. Let's check R line 131: names(...) <- c(... "Costo ($)")
        # Maybe the dataframe passed to Distrib_tolvas has different structural context?
        # In Distrib_tolvas(tabla1...), tabla1 comes from recomendation().
        # In R: tabla1 names are "Unidades","Kg/Ha","Kg totales","Bultos","Costo ($)","Unidades_refuerzo"
        # So column 5 IS Cost. Why would they multiply Cost * vec?
        # Line 1047: combinaciones$Var1 <- Dosis * combinaciones$Var1
        # Line 1068: Autonomia$Var1 <- 500 / combinaciones$Var1
        # If Dosis is Cost, calculating Autonomy (Distance/Capacity?) on Cost seems weird.
        # BUT, looking at line 1253 in shape_verion: dosis_mot <- recomen$`Kg/Ha-Real`.
        # Ah, Distrib_tolvas output columns include Kg/Ha-Real.
        # Let's assume Dosis SHOULD BE Kg/Ha (Column 2 in R logic, or maybe the code has shifted cols).
        # Let's look really closely at R line 1042: Dosis<-tabla[1,5]
        # And line 130: tabla_recomendacion[1,5]<-... Costo.
        # It is extremely likely this is a bug in the original R code OR I am misinterpreting the column index.
        # However, purely physically, you distribute MASS (Kg/Ha) into hoppers, not Dollars.
        # So I will use 'Kg/Ha' for the calculation.
        
        target_dose = float(recommendation_table.iloc[0]['Kg/Ha'])
        
        # Expand grid for 3 hoppers (Var1, Var2, Var3) summing to 1 (100% of dose)
        combos = [c for c in itertools.product(vec, repeat=3) if abs(sum(c) - 1.0) < 0.001]
        
        valid_combos = []
        for c in combos:
            # Calculate actual dose per hopper
            doses = [target_dose * x for x in c]
            
            # Filter rule: < 70 and > 0 (R line 1053)
            # a<-which(combinaciones... < 70 & ... > 0)
            # if(length(a)>0) -> exclude.
            # So we WANT combos where NO hopper is between 0 and 70? 
            # Or we exclude if ANY hopper is in that range?
            # R: if length(a) > 0 -> v = c(v, i) -> combinaciones[-v,].
            # So we REMOVE rows where any value is (0, 70).
            # Meaning valid values must be either 0 OR >= 70.
            
            if any(0 < d < 70 for d in doses):
                continue
            
            valid_combos.append(c)
            
        if not valid_combos:
            # Fallback (R keeps 'combinaciones' if v is empty)
            # If everything filtered out, use all original summing to 1.
            valid_combos = combos
        
        # Calculate Autonomy
        # Autonomia$Var1 <- 500 / dose1
        # Autonomia$Var2 <- 300 / dose2
        # Autonomia$Var3 <- 300 / dose3
        # suma <- min(autonomy columns) -> wait, R says apply(..., 1, min)
        # then which.max(suma). Maximizing the minimum autonomy (bottleneck).
        
        best_score = -1
        
        for c in valid_combos:
            d1 = target_dose * c[0]
            d2 = target_dose * c[1]
            d3 = target_dose * c[2]
            
            # Avoid div by zero
            a1 = 500/d1 if d1 > 0 else 99999
            a2 = 300/d2 if d2 > 0 else 99999
            a3 = 300/d3 if d3 > 0 else 99999
            
            min_autonomy = min(a1, a2, a3)
            
            if min_autonomy > best_score:
                best_score = min_autonomy
                best_combo = c

        return {
            "TOLVA 1": round(best_combo[0] * target_dose, 2),
            "TOLVA 2": round(best_combo[1] * target_dose, 2),
            "TOLVA 3": round(best_combo[2] * target_dose, 2),
            "Kg/Ha-Real": target_dose # Assuming total match
        }

    elif num_products == 2:
        # Implementation for 2 products (R lines 1076+)
        # This is more complex involving permutations of product placement in hoppers.
        # We will simplify for the prototype but aim to support it.
        dosis1 = float(recommendation_table.iloc[0]['Kg/Ha'])
        dosis2 = float(recommendation_table.iloc[1]['Kg/Ha'])
        
        # R logic: sum of factors = 2.
        # Tries to assign products to hoppers (1,2,3).
        # We need to port this carefully later. 
        # For now, returning a placeholder or basic split.
        logger.info("2-Product optimization logic pending strict porting.")
        return {
            "TOLVA 1": dosis1,
            "TOLVA 2": dosis2,
            "TOLVA 3": 0
        }

    return {}

def apply_hopper_distribution_to_shape(gdf, hopper_config):
    """
    Applies the hopper distribution (Target Doses) to the spatial grid.
    Replicates 'shape_verion' from R.
    
    Args:
        gdf (GeoDataFrame): Must contain 'Dosis' column (Nitrogen/Units spatial).
        hopper_config (dict): Output from distribute_hoppers (e.g. {'TOLVA 1': 100, ...})
        
    Returns:
        GeoDataFrame: Updated with 'M1', 'M2', 'M3' columns.
    """
    if not hopper_config or gdf.empty:
        return gdf
        
    motors = ["M1", "M2", "M3"]
    keys = ["TOLVA 1", "TOLVA 2", "TOLVA 3"]
    
    # R Logic:
    # dosis_mot <- recomen$`Kg/Ha-Real` (The target total dose)
    # prom <- mean(shape@data$Dosis) (The mean of the spatial dose)
    # diff = Target - Mean
    # Motor = SpatialDose + Abs(diff) (if diff >= 0) else SpatialDose - Abs(diff)
    # Which simplifies to: Motor = SpatialDose + (Target - Mean)
    # i.e. We shift the spatial curve so its new mean is the Target.
    
    spatial_mean = gdf['Dosis'].mean()
    
    # Iterate through hoppers/motors
    for m, k in zip(motors, keys):
        target_val = hopper_config.get(k, 0)
        
        # If target is ~0 or NA, set column to 0
        if pd.isna(target_val) or target_val <= 0:
            gdf[m] = 0
            continue
            
        # Shift Logic
        diff = target_val - spatial_mean
        gdf[m] = gdf['Dosis'] + diff
        
        # Min limit check (R line 1269: val_m50 <- which(... < 50))
        # If < 50, set to 50, then re-adjust mean?
        # R Logic: 
        #   shape[pts < 50] <- 50
        #   prom1 <- mean(shape)
        #   dif <- target - prom1
        #   shape <- shape + dif (Re-shift to match target mean)
        
        mask_low = gdf[m] < 50
        if mask_low.any():
            gdf.loc[mask_low, m] = 50
            # Re-calculate mean after clamping
            current_mean = gdf[m].mean()
            diff_new = target_val - current_mean
            gdf[m] = gdf[m] + diff_new
            
    return gdf
