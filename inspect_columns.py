import pandas as pd
file_path = r'c:\Users\sacorreac\OneDrive - Sector Agro\AP\scripts\4_antigravity\BD_Informes_Fertilizacion_modelo.xlsx'
df = pd.read_excel(file_path)
print("COLUMNS:")
print(df.columns.tolist())
print("\nFIRST 5 ROWS:")
print(df.head())
