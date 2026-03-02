import pandas as pd
file_path = r'c:\Users\sacorreac\OneDrive - Sector Agro\AP\scripts\4_antigravity\BD_Informes_Fertilizacion_modelo.xlsx'
df = pd.read_excel(file_path)
print("COLUMNS FOUND:")
for col in df.columns:
    print(f"- '{col}'")
print("\nFIRST ROW:")
print(df.iloc[0].to_dict())
