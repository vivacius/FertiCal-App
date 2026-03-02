"""
Query Engine for Sam IA - Local data queries without OpenAI
Handles common questions directly from the DataFrame
"""
import pandas as pd
import re

def extract_suerte_number(question):
    """Extract suerte number from question"""
    match = re.search(r'\b(\d{3}[A-Z]?)\b', question)
    return match.group(1) if match else None

def extract_hacienda_number(question):
    """Extract hacienda number from question"""
    match = re.search(r'hacienda\s+(\d+)', question, re.IGNORECASE)
    return match.group(1) if match else None

def extract_motor_number(question):
    """Extract motor number from question"""
    match = re.search(r'motor\s+(\d+)', question, re.IGNORECASE)
    return match.group(1) if match else None

def query_local(question, df):
    """
    Try to answer question using local DataFrame queries
    Returns (answer, used_local) tuple
    """
    question_lower = question.lower()
    
    # Normalized keywords for easier matching
    q = question_lower.replace('-', ' ').replace('á', 'a').replace('ó', 'o').replace('í', 'i').replace('ú', 'u').replace('é', 'e')
    
    # helper for classification names
    class_opt = 'Óptima'
    class_sobre = 'Sobre'
    class_sub = 'Sub'

    # Filter for area data
    df_area = df[df['Métrica'].isin(['Area', 'Área'])]
    df_quality = df_area[df_area['Clasificación'].isin([class_sobre, class_sub, class_opt])]
    
    # Query: What does over-application mean?
    if 'que significa' in q and ('sobre aplicacion' in q or 'tanta sobre' in q):
        return ("La sobre-aplicación ocurre cuando el equipo aplica una dosis de fertilizante mayor al rango considerado 'Óptimo' (usualmente >15% de desvío positivo). "
                "Esto implica un desperdicio de insumos, mayores costos y puede afectar negativamente el desarrollo del cultivo si el exceso es extremo. ⚠️"), True

    # Query 1: When was suerte X applied?
    if 'cuando' in q or 'fecha' in q:
        suerte_num = extract_suerte_number(question)
        hacienda_num = extract_hacienda_number(question)
        
        if suerte_num:
            query_df = df[df['Suerte'] == suerte_num]
            if hacienda_num:
                query_df = query_df[query_df['Hacienda'] == int(hacienda_num)]
            
            if not query_df.empty:
                fecha_min = query_df['Fecha_Labor'].min()
                fecha_max = query_df['Fecha_Labor'].max()
                hacienda = query_df['Hacienda'].iloc[0]
                zona = query_df['Zona'].iloc[0]
                
                if fecha_min == fecha_max:
                    answer = f"La suerte {suerte_num} (Hacienda {hacienda}, {zona}) fue aplicada el {fecha_min.strftime('%d de %B de %Y')}. 🌾"
                else:
                    answer = f"La suerte {suerte_num} (Hacienda {hacienda}, {zona}) fue aplicada entre el {fecha_min.strftime('%d de %B de %Y')} y el {fecha_max.strftime('%d de %B de %Y')}. 🌾"
                return answer, True
            else:
                return f"No encontré la suerte {suerte_num} en los datos actuales. Verifica los filtros. 🔍", True
    
    # Query: Count suertes
    if 'cuantas suertes' in q or 'numero de suertes' in q:
        num_suertes = df['Suerte'].nunique()
        return f"Se han trabajado {num_suertes} suertes diferentes en el periodo seleccionado. 📊", True

    # Query: Best/Worst Zone
    if 'zona' in q and ('mejor' in q or 'peor' in q or 'mas sobre' in q or 'calidad' in q):
        df_kpis = df_quality[df_quality['Motor'] == 'Total']
        if not df_kpis.empty:
            zone_stats = df_kpis.groupby(['Zona', 'Clasificación'])['Valor'].sum().unstack(fill_value=0)
            if class_opt not in zone_stats.columns: zone_stats[class_opt] = 0
            if class_sobre not in zone_stats.columns: zone_stats[class_sobre] = 0
            
            zone_stats['Total'] = zone_stats.sum(axis=1)
            zone_stats['% Optima'] = (zone_stats[class_opt] / zone_stats['Total'] * 100)
            zone_stats['% Sobre'] = (zone_stats[class_sobre] / zone_stats['Total'] * 100)
            
            if 'mejor' in q or 'mejor calidad' in q:
                best_z = zone_stats['% Optima'].idxmax()
                best_val = zone_stats['% Optima'].max()
                return f"La zona con mejor calidad de aplicación es **{best_z}** con un {best_val:.1f}% de calidad óptima. ✅", True
            elif 'mas sobre' in q or 'peor' in q or 'sobre aplicacion' in q:
                worst_z = zone_stats['% Sobre'].idxmax()
                worst_val = zone_stats['% Sobre'].max()
                return f"La zona con mayor sobre-aplicación es **{worst_z}** con un {worst_val:.1f}%. ⚠️", True

    # Query: Motor Rankings / Best-Worst Motor
    if 'motor' in q:
        df_motors = df_quality[~df_quality['Motor'].isin(['Total', 'No aplica'])]
        if not df_motors.empty:
            motor_stats = df_motors.groupby(['Motor', 'Clasificación'])['Valor'].sum().unstack(fill_value=0)
            if class_opt not in motor_stats.columns: motor_stats[class_opt] = 0
            if class_sobre not in motor_stats.columns: motor_stats[class_sobre] = 0
            
            motor_stats['Total'] = motor_stats.sum(axis=1)
            motor_stats['% Optima'] = (motor_stats[class_opt] / motor_stats['Total'] * 100)
            motor_stats['% Sobre'] = (motor_stats[class_sobre] / motor_stats['Total'] * 100)
            
            motor_num = extract_motor_number(question)
            if motor_num and ('hectareas' in q or 'hizo' in q or 'desempeño' in q):
                matching_motors = [m for m in motor_stats.index if str(motor_num) in str(m)]
                if matching_motors:
                    m_idx = matching_motors[0]
                    row = motor_stats.loc[m_idx]
                    return f"El **{m_idx}** trabajó {row['Total']:,.1f} ha, con {row['% Optima']:.1f}% de calidad óptima y {row['% Sobre']:.1f}% de sobre-aplicación. 🚜", True

            if 'mejor' in q or 'calidad' in q or 'eficiente' in q:
                if 'ranking' in q or 'lista' in q or 'cuales' in q:
                    top_m = motor_stats.sort_values('% Optima', ascending=False).head(3)
                    res = "**Ranking de motores por calidad óptima:**\n\n"
                    for i, (name, row) in enumerate(top_m.iterrows(), 1):
                        res += f"{i}. **{name}**: {row['% Optima']:.1f}% ✅\n"
                    return res, True
                else:
                    best_m = motor_stats['% Optima'].idxmax()
                    best_val = motor_stats['% Optima'].max()
                    return f"El **{best_m}** tiene el mejor desempeño con {best_val:.1f}% de calidad óptima. 🚜✨", True
            
            if 'sobre aplicacion' in q or 'peor' in q or 'atencion' in q:
                if 'ranking' in q or 'lista' in q or 'cuales' in q:
                    worst_m = motor_stats.sort_values('% Sobre', ascending=False).head(3)
                    res = "**Motores con mayor sobre-aplicación (requieren atención):**\n\n"
                    for i, (name, row) in enumerate(worst_m.iterrows(), 1):
                        res += f"{i}. **{name}**: {row['% Sobre']:.1f}% ⚠️\n"
                    return res, True
                else:
                    worst_m = motor_stats['% Sobre'].idxmax()
                    worst_val = motor_stats['% Sobre'].max()
                    return f"El **{worst_m}** es el que presenta más sobre-aplicación con {worst_val:.1f}%. ⚠️", True

    # Query: Suerte Rankings / Best-Worst Suerte
    if 'suerte' in q:
        df_kpis = df_quality[df_quality['Motor'] == 'Total']
        if not df_kpis.empty:
            suerte_stats = df_kpis.groupby(['Suerte', 'Hacienda', 'Zona', 'Clasificación'])['Valor'].sum().unstack(fill_value=0).reset_index()
            if class_opt not in suerte_stats.columns: suerte_stats[class_opt] = 0
            if class_sobre not in suerte_stats.columns: suerte_stats[class_sobre] = 0
            
            suerte_stats['Total'] = suerte_stats[class_opt] + suerte_stats[class_sobre] + suerte_stats.get(class_sub, 0)
            suerte_stats['% Optima'] = (suerte_stats[class_opt] / suerte_stats['Total'] * 100)
            suerte_stats['% Sobre'] = (suerte_stats[class_sobre] / suerte_stats['Total'] * 100)
            
            if 'sobre aplicacion' in q or 'peor' in q or 'mayor sobre' in q:
                n = 3 if '3' in q or 'ranking' in q or 'cuales' in q else 1
                top_s = suerte_stats.sort_values('% Sobre', ascending=False).head(n)
                if n > 1:
                    res = f"**Ranking de suertes con más sobre-aplicación:**\n\n"
                    for i, (_, row) in enumerate(top_s.iterrows(), 1):
                        res += f"{i}. **Suerte {row['Suerte']}** ({row['Zona']}): {row['% Sobre']:.1f}% ⚠️\n"
                    return res, True
                else:
                    row = top_s.iloc[0]
                    return f"La suerte con mayor sobre-aplicación es **{row['Suerte']}** (Hacienda {row['Hacienda']}, {row['Zona']}) con {row['% Sobre']:.1f}%. ⚠️", True
            
            if 'mejor' in q or 'calidad' in q:
                best_s = suerte_stats.sort_values('% Optima', ascending=False).head(1)
                row = best_s.iloc[0]
                return f"La suerte con mejor calidad es **{row['Suerte']}** ({row['Zona']}) con {row['% Optima']:.1f}% óptima. ✅", True

    # Query: Unidades / Recomendacion for Suerte
    if ('unidad' in q or 'recomendad' in q or 'recomendacion' in q):
        suerte_num = extract_suerte_number(question)
        if suerte_num and 'Unidades' in df.columns and 'Fecha_Recomendacion' in df.columns:
            query_df = df[df['Suerte'] == suerte_num]
            hacienda_num = extract_hacienda_number(question)
            if hacienda_num:
                query_df = query_df[query_df['Hacienda'] == int(hacienda_num) if hacienda_num.isdigit() else hacienda_num]
                
            if not query_df.empty:
                unidades = query_df['Unidades'].iloc[0]
                fecha_rec = query_df['Fecha_Recomendacion'].iloc[0]
                hacienda = query_df['Hacienda'].iloc[0]
                zona = query_df['Zona'].iloc[0]
                
                if pd.notnull(fecha_rec) and pd.notnull(unidades):
                    if isinstance(fecha_rec, str):
                        fecha_str = fecha_rec
                    else:
                        fecha_str = fecha_rec.strftime('%d de %B de %Y')
                    return f"Para la suerte {suerte_num} (Hacienda {hacienda}, {zona}), se recomendaron **{unidades:.1f} unidades** el **{fecha_str}**. 📋", True
                else:
                    return f"La suerte {suerte_num} (Hacienda {hacienda}) no tiene información de recomendación registrada. ❌", True

    # Query: Global Metrics
    df_kpis = df_quality[df_quality['Motor'] == 'Total']
    total_area = df_kpis['Valor'].sum()
    
    if 'area total' in q or 'hectareas' in q:
        return f"El área total fertilizada es de {total_area:,.1f} hectáreas. 🌾", True
    
    if 'calidad optima' in q or 'porcentaje optimo' in q:
        optima = df_kpis[df_kpis['Clasificación'] == class_opt]['Valor'].sum()
        pct = (optima / total_area * 100) if total_area else 0
        return f"La calidad óptima global es del {pct:.1f}% ({optima:,.1f} ha de {total_area:,.1f} ha). ✅", True
    
    if 'sobre aplicacion' in q or 'cuanta sobre' in q:
        sobre = df_kpis[df_kpis['Clasificación'] == class_sobre]['Valor'].sum()
        pct = (sobre / total_area * 100) if total_area else 0
        return f"La sobre-aplicación global es del {pct:.1f}% ({sobre:,.1f} ha de {total_area:,.1f} ha). ⚠️", True

    if 'sub aplicacion' in q or 'cuanta sub' in q:
        sub = df_kpis[df_kpis['Clasificación'] == class_sub]['Valor'].sum()
        pct = (sub / total_area * 100) if total_area else 0
        return f"La sub-aplicación global es del {pct:.1f}% ({sub:,.1f} ha de {total_area:,.1f} ha). 📉", True

    # Summary
    if q in ['resumen', 'resume', 'dame un resumen', 'resumen general']:
        optima = df_kpis[df_kpis['Clasificación'] == class_opt]['Valor'].sum()
        sobre = df_kpis[df_kpis['Clasificación'] == class_sobre]['Valor'].sum()
        sub = df_kpis[df_kpis['Clasificación'] == class_sub]['Valor'].sum()
        pct_opt = (optima / total_area * 100) if total_area else 0
        return f"📊 **Resumen General:**\n- Área: {total_area:,.1f} ha\n- Calidad Óptima: {pct_opt:.1f}%\n- Sobre-aplicación: {(sobre/total_area*100 if total_area else 0):.1f}%\n- Sub-aplicación: {(sub/total_area*100 if total_area else 0):.1f}%", True

    # No local match found
    return None, False
