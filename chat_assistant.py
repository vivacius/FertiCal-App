"""
AI Chat Assistant Module for Fertilization Dashboard
Uses OpenAI API to answer questions about the data
"""
import pandas as pd
from openai import OpenAI

def generate_data_context(df):
    """
    Generate a concise summary of the current filtered data
    to provide context to the AI model
    """
    if df.empty:
        return "No hay datos disponibles con los filtros actuales."
    
    # Filter for quality metrics
    df_area = df[df['Métrica'].isin(['Area', 'Área'])]
    df_quality = df_area[df_area['Clasificación'].isin(['Sobre', 'Sub', 'Óptima'])]
    df_kpis = df_quality[df_quality['Motor'] == 'Total']
    
    # Calculate key metrics
    total_area = df_kpis['Valor'].sum()
    optima_val = df_kpis[df_kpis['Clasificación'] == 'Óptima']['Valor'].sum()
    sobre_val = df_kpis[df_kpis['Clasificación'] == 'Sobre']['Valor'].sum()
    sub_val = df_kpis[df_kpis['Clasificación'] == 'Sub']['Valor'].sum()
    
    pct_opt = (optima_val / total_area * 100) if total_area else 0
    pct_sobre = (sobre_val / total_area * 100) if total_area else 0
    pct_sub = (sub_val / total_area * 100) if total_area else 0
    
    # Get top problematic suertes with more detail
    pivot_geo = df_kpis.groupby(['Zona', 'Hacienda', 'Suerte', 'Clasificación'])['Valor'].sum().unstack(fill_value=0).reset_index()
    for col in ['Óptima', 'Sobre', 'Sub']:
        if col not in pivot_geo.columns:
            pivot_geo[col] = 0
    pivot_geo['Total App'] = pivot_geo['Óptima'] + pivot_geo['Sobre'] + pivot_geo['Sub']
    pivot_geo['% Sobre'] = (pivot_geo['Sobre'] / pivot_geo['Total App'] * 100).fillna(0)
    pivot_geo['% Sub'] = (pivot_geo['Sub'] / pivot_geo['Total App'] * 100).fillna(0)
    
    top_sobre = pivot_geo.nlargest(3, '% Sobre')[['Zona', 'Hacienda', 'Suerte', '% Sobre']].to_dict('records')
    top_sub = pivot_geo.nlargest(3, '% Sub')[['Zona', 'Hacienda', 'Suerte', '% Sub']].to_dict('records')
    
    # Get date information for ALL suertes with hacienda
    has_rec = 'Fecha_Recomendacion' in df.columns and 'Unidades' in df.columns
    if has_rec:
        suerte_info = df.groupby(['Suerte', 'Hacienda', 'Zona']).agg(
            Fecha_Min=('Fecha_Labor', 'min'),
            Fecha_Max=('Fecha_Labor', 'max'),
            Fecha_Rec=('Fecha_Recomendacion', 'first'),
            Unidades=('Unidades', 'first')
        ).reset_index()
    else:
        suerte_info = df.groupby(['Suerte', 'Hacienda', 'Zona']).agg(
            Fecha_Min=('Fecha_Labor', 'min'),
            Fecha_Max=('Fecha_Labor', 'max')
        ).reset_index()
    
    # Create a detailed list of all suertes
    all_suertes_info = []
    for _, row in suerte_info.iterrows():
        fecha_str = f"{row['Fecha_Min'].strftime('%Y-%m-%d')}"
        if row['Fecha_Min'] != row['Fecha_Max']:
            fecha_str += f" a {row['Fecha_Max'].strftime('%Y-%m-%d')}"
            
        rec_info = ""
        if has_rec and pd.notnull(row['Fecha_Rec']):
            rec_str = row['Fecha_Rec'] if isinstance(row['Fecha_Rec'], str) else row['Fecha_Rec'].strftime('%Y-%m-%d')
            unid_val = f"{row['Unidades']:.1f}" if pd.notnull(row['Unidades']) else "N/A"
            rec_info = f" | Rec: {unid_val} unid. el {rec_str}"
            
        all_suertes_info.append(f"{row['Suerte']} (Hacienda {row['Hacienda']}, {row['Zona']}): {fecha_str}{rec_info}")
    
    # Motor performance with detailed metrics
    df_motors = df_quality[~df_quality['Motor'].isin(['Total', 'No aplica'])]
    motor_stats = df_motors.groupby(['Motor', 'Clasificación'])['Valor'].sum().unstack(fill_value=0)
    
    motor_details = []
    for motor in motor_stats.index:
        total_motor = motor_stats.loc[motor].sum()
        optima_motor = motor_stats.loc[motor].get('Óptima', 0)
        sobre_motor = motor_stats.loc[motor].get('Sobre', 0)
        sub_motor = motor_stats.loc[motor].get('Sub', 0)
        
        pct_opt_motor = (optima_motor / total_motor * 100) if total_motor else 0
        pct_sobre_motor = (sobre_motor / total_motor * 100) if total_motor else 0
        
        motor_details.append(f"- {motor}: {total_motor:.1f} ha ({pct_opt_motor:.1f}% óptima, {pct_sobre_motor:.1f}% sobre-aplicación)")
    
    # Date range
    date_min = df['Fecha_Labor'].min().strftime('%Y-%m-%d')
    date_max = df['Fecha_Labor'].max().strftime('%Y-%m-%d')
    
    context = f"""
Datos actuales del dashboard de fertilización:

PERÍODO DE DATOS: {date_min} hasta {date_max}

RESUMEN GENERAL:
- Área total fertilizada: {total_area:,.1f} hectáreas
- Calidad óptima: {pct_opt:.1f}%
- Sobre-aplicación: {pct_sobre:.1f}%
- Sub-aplicación: {pct_sub:.1f}%

DESEMPEÑO POR MOTOR:
{chr(10).join(motor_details)}

TOP 3 SUERTES CON MAYOR SOBRE-APLICACIÓN:
{chr(10).join([f"- {s['Suerte']} ({s['Zona']}, {s['Hacienda']}): {s['% Sobre']:.1f}%" for s in top_sobre])}

TOP 3 SUERTES CON MAYOR SUB-APLICACIÓN:
{chr(10).join([f"- {s['Suerte']} ({s['Zona']}, {s['Hacienda']}): {s['% Sub']:.1f}%" for s in top_sub])}

LISTADO COMPLETO DE SUERTES CON FECHAS:
{chr(10).join(['- ' + info for info in all_suertes_info[:20]])}
{"... (y más suertes disponibles)" if len(all_suertes_info) > 20 else ""}
"""
    return context.strip()

def query_openai(user_message, context, api_key):
    """
    Send a query to OpenAI with data context
    """
    try:
        client = OpenAI(api_key=api_key)
        
        system_prompt = """Eres Sam IA, un asistente experto y amigable en agricultura de precisión, especializado en análisis de fertilización de caña de azúcar.
Tu personalidad es profesional pero cercana, siempre dispuesto a ayudar.
Cuando te presentes, di algo como "¡Hola! Soy Sam IA, tu asistente de agricultura de precisión. ¿En qué puedo ayudarte hoy?"
Usa los datos proporcionados en el contexto para dar respuestas precisas y útiles.
Si no tienes información suficiente, indícalo claramente pero ofrece alternativas.
Responde en español de forma amigable, clara y profesional.
Usa emojis ocasionalmente para ser más expresivo (🌾, 📊, 🚜, etc.)."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Cambiado de gpt-4 para reducir costos ~12x
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexto de datos:\n{context}\n\nPregunta del usuario: {user_message}"}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error al consultar OpenAI: {str(e)}"
