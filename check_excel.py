import pandas as pd

file = r'c:\Users\sacorreac\OneDrive - Sector Agro\AP\scripts\4_antigravity\BD_Informes_Fertilizacion_con_recomendacion.xlsx'
df = pd.read_excel(file)
print("Columns:")
for col in df.columns:
    print(f" - {col}")
print("\nSample 'Total' rows:")
print(df[df['Motor'] == 'Total'][['Suerte', 'Fecha_Recomendacion', 'Unidades']].head())
