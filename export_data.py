import pandas as pd
import json
import numpy as np

FILE_PATH = r'c:\Users\sacorreac\OneDrive - Sector Agro\AP\scripts\4_antigravity\BD_Informes_Fertilizacion_modelo.xlsx'
OUTPUT_PATH = r'c:\Users\sacorreac\OneDrive - Sector Agro\AP\scripts\4_antigravity\dashboard_data.json'

def convert_df(df):
    return df.where(pd.notnull(df), None).to_dict(orient='records')

try:
    print(f"Reading {FILE_PATH}...")
    df = pd.read_excel(FILE_PATH)
    
    # Pre-processing dates to string
    df['Fecha_Labor'] = df['Fecha_Labor'].astype(str)
    
    # Fill NAs
    df['Motor'] = df['Motor'].fillna('Desconocido')
    
    # Create a structured object to reduce frontend processing overhead if needed, 
    # but initially flat JSON is fine for smallish datasets.
    # Let's export the raw records and do aggregation in JS (more flexible for filters)
    
    data = convert_df(df)
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully exported {len(data)} records to {OUTPUT_PATH}")

except Exception as e:
    print(f"Error converting data: {e}")
