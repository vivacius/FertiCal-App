"""
Script to upload Excel fertilization data to Supabase.
Requires: pip install pandas supabase openpyxl
"""
import pandas as pd
from supabase import create_client, Client
import os

# --- CONFIGURATION ---
from supabase_config import SUPABASE_URL, SUPABASE_KEY
EXCEL_FILE = r'c:\Users\sacorreac\OneDrive - Sector Agro\AP\scripts\4_antigravity\BD_Informes_Fertilizacion_con_recomendacion.xlsx'

def upload_data():

    print(f"📖 Reading Excel: {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE, dtype={'Hacienda': str})
    print(df.columns.tolist())
    df.columns = (
        df.columns
        .str.strip()        # quita espacios
        .str.replace(' ', '_')
    )

    # Pre-processing: Standardize column names to match SQL schema
    df = df.rename(columns={
        'Fecha_Labor': 'fecha_labor',
        'Año': 'año',
        'Mes': 'mes',
        'Zona': 'zona',
        'Hacienda': 'hacienda',
        'Hac_ste': 'hac_ste',
        'Suerte': 'suerte',
        'Motor': 'motor',
        'Tipo': 'tipo',
        'Métrica': 'metrica',
        'Clasificación': 'clasificacion',
        'Valor': 'valor',
        'Area_ste': 'area_ste',
        'Area_aplicada': 'area_aplicada',
        'Fecha_Recomendacion': 'fecha_recomendacion',
        'Unidades': 'unidades'
    })

    # Keep only columns that are in the schema
    schema_cols = [
        'fecha_labor', 'año', 'mes', 'zona', 'hacienda', 'hac_ste', 
        'suerte', 'motor', 'tipo', 'metrica', 'clasificacion', 
        'valor', 'area_ste', 'area_aplicada', 'fecha_recomendacion', 'unidades'
    ]
    df = df[schema_cols]

    # Convert dates to string for JSON serialization
    df['fecha_labor'] = df['fecha_labor'].dt.strftime('%Y-%m-%d')
    if 'fecha_recomendacion' in df.columns:
        df['fecha_recomendacion'] = pd.to_datetime(df['fecha_recomendacion'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Handle NaN and Inf values more robustly
    import numpy as np
    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)

    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Chunking for large datasets
    batch_size = 1000
    total_rows = len(df)
    
    print(f"🚀 Uploading {total_rows} rows to Supabase in batches of {batch_size}...")
    
    for i in range(0, total_rows, batch_size):
        batch_df = df.iloc[i:i+batch_size].copy()
        # Ensure everything is serializable
        batch = batch_df.to_dict(orient="records")
        
        # Double check for any remaining NaNs that might have slipped through
        clean_batch = []
        for row in batch:
            clean_row = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            clean_batch.append(clean_row)

        try:
            supabase.table("fertilization_data").insert(clean_batch).execute()
            print(f"✅ Uploaded {min(i+batch_size, total_rows)}/{total_rows} rows")
        except Exception as e:
            print(f"❌ Error in batch {i}: {e}")
            break

    print("🎉 Migration complete!")

if __name__ == "__main__":
    upload_data()
