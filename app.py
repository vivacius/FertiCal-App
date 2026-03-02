import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Dashboard Fertilización de Precisión",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLES ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2E7D32;
    }
    .metric-sub {
        font-size: 12px;
        color: #888;
    }
    .stHeader {
        color: #1b5e20;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADER ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        # Ensure correct types
        df['Fecha_Labor'] = pd.to_datetime(df['Fecha_Labor'])
        # Handle 'No aplica' in Motor or other categorical
        df['Motor'] = df['Motor'].fillna('Desconocido')
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

FILE_PATH = r'c:\Users\sacorreac\OneDrive - Sector Agro\AP\scripts\4_antigravity\BD_Informes_Fertilizacion_modelo.xlsx'
df = load_data(FILE_PATH)

if df.empty:
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filtros Operativos")

# Year and Month
all_years = sorted(df['Año'].dropna().unique())
selected_year = st.sidebar.selectbox("Año", all_years, index=len(all_years)-1 if all_years else 0)

# Filter by year first to update months
df_year = df[df['Año'] == selected_year]
all_months = sorted(df_year['Mes'].dropna().unique())
selected_month = st.sidebar.multiselect("Mes", all_months, default=all_months)

if not selected_month:
    df_filtered_time = df_year
else:
    df_filtered_time = df_year[df_year['Mes'].isin(selected_month)]

# Geographic Filters
all_zonas = sorted(df_filtered_time['Zona'].dropna().unique())
selected_zona = st.sidebar.multiselect("Zona", all_zonas, default=all_zonas)

# Filter by zona for haciendas
if selected_zona:
    df_zona = df_filtered_time[df_filtered_time['Zona'].isin(selected_zona)]
else:
    df_zona = df_filtered_time

all_haciendas = sorted(df_zona['Hacienda'].dropna().unique())
selected_hacienda = st.sidebar.multiselect("Hacienda", all_haciendas) # Default empty = all? better select none for all to save space

# Apply filters
df_main = df_zona.copy()
if selected_hacienda:
    df_main = df_main[df_main['Hacienda'].isin(selected_hacienda)]

# Motor Filter
all_motores = sorted(df_main['Motor'].dropna().unique())
selected_motor = st.sidebar.multiselect("Motor", all_motores, default=all_motores)
if selected_motor:
    df_main = df_main[df_main['Motor'].isin(selected_motor)]


# --- KPI CALCULATIONS ---
# The data is in long format per metric/classification.
# We need to aggregate properly. 
# Assuming 'Area_ste' is repeated for each atom, we should be careful summing it.
# Usually 'Area_ste' is an attribute of the Suerte.
# To get total Area Fertilizada (Area_aplicada), we need to sum 'Valor' where Metric is Area? 
# Or is 'Area_aplicada' a column? Yes, 'Area_aplicada' is a column.
# Let's check atomic level: "Cada fila representa una métrica atómica"
# If we have rows for "Sobre", "Sub", "Optima" for the SAME Suerte/Motor/Fecha, 
# 'Area_aplicada' might be the sum of those values? 
# OR 'Area_aplicada' is the total applied and 'Valor' is the breakdown?
# Let's assume 'Valor' is the area for that specific classification if Metrica == 'Area'.

# Filter for Area metrics
df_area_metrics = df_main[(df_main['Métrica'] == 'Area')]
df_pct_metrics = df_main[(df_main['Métrica'] == 'Porcentaje')]

# Total Area Fertilizada (Sum of Valor for all classifications related to application?)
# Classifications: Sobre, Sub, Óptima. 
# Avoid double counting if there are other classifications.
valid_classifs = ['Sobre', 'Sub', 'Óptima']
df_calidad = df_area_metrics[df_area_metrics['Clasificación'].isin(valid_classifs)]

total_area_fertilizada = df_calidad['Valor'].sum()

# Area Optima
area_optima = df_calidad[df_calidad['Clasificación'] == 'Óptima']['Valor'].sum()
pct_global_optima = (area_optima / total_area_fertilizada * 100) if total_area_fertilizada > 0 else 0

# Area Sobre
area_sobre = df_calidad[df_calidad['Clasificación'] == 'Sobre']['Valor'].sum()
pct_global_sobre = (area_sobre / total_area_fertilizada * 100) if total_area_fertilizada > 0 else 0

# Area Sub
area_sub = df_calidad[df_calidad['Clasificación'] == 'Sub']['Valor'].sum()
pct_global_sub = (area_sub / total_area_fertilizada * 100) if total_area_fertilizada > 0 else 0

# Cobertura
# Cobertura = Area_aplicada / Area_ste. 
# We need distinct Suertes to sum Area_ste and Area_aplicada correctly.
# df_main has duplicates for Suerte because of the breakdown rows.
# creating distinct suertes df
df_suertes_unique = df_main[['Hacienda', 'Suerte', 'Fecha_Labor', 'Area_ste', 'Area_aplicada']].drop_duplicates()
total_area_ste = df_suertes_unique['Area_ste'].sum()
total_area_aplicada_real = df_suertes_unique['Area_aplicada'].sum()
cobertura_global = (total_area_aplicada_real / total_area_ste * 100) if total_area_ste > 0 else 0

num_suertes = df_suertes_unique['Suerte'].nunique()


# --- DASHBOARD LAYOUT ---

st.title("🚜 Dashboard de Fertilización de Precisión")
st.markdown("### Resumen Ejecutivo")

# KPI Cards
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.metric("Área Fertilizada", f"{total_area_fertilizada:,.1f} ha")
with kpi2:
    st.metric("Área Óptima", f"{pct_global_optima:.1f}%", delta=None)
with kpi3:
    st.metric("Área Sobre", f"{pct_global_sobre:.1f}%", delta_color="inverse")
with kpi4:
    st.metric("Área Sub", f"{pct_global_sub:.1f}%", delta_color="inverse")
with kpi5:
    st.metric("Cobertura Labor", f"{cobertura_global:.1f}%", help="Area Aplicada / Area Suerte")


# TABS FOR NARRATIVE
tab_quality, tab_motor, tab_speed, tab_geo = st.tabs(["📊 Calidad de Aplicación", "🚜 Análisis por Motor", "⚡ Velocidad", "🗺️ Territorio"])

# --- TAB 1: CALIDAD ---
with tab_quality:
    st.subheader("Evolución y Distribución de Calidad")
    
    col_q1, col_q2 = st.columns([2, 1])
    
    with col_q1:
        # Time evolution
        # Aggregate by Month-Year
        df_time = df_calidad.copy()
        df_time['Periodo'] = df_time['Fecha_Labor'].dt.to_period('M').astype(str)
        df_evol = df_time.groupby(['Periodo', 'Clasificación'])['Valor'].sum().reset_index()
        
        # Calculate % for each period to make it 100% stacked or just Area
        # Stacked Bar 100% is better for Quality stability
        
        fig_evol = px.bar(df_evol, x='Periodo', y='Valor', color='Clasificación',
                          title="Evolución de Calidad (Área)",
                          color_discrete_map={'Óptima': '#2E7D32', 'Sobre': '#D32F2F', 'Sub': '#1976D2'},
                          barmode='stack')
        st.plotly_chart(fig_evol, use_container_width=True)
        
    with col_q2:
        # Donut Chart Global
        df_donut = df_calidad.groupby('Clasificación')['Valor'].sum().reset_index()
        fig_donut = px.pie(df_donut, values='Valor', names='Clasificación',
                           title="Distribución Global",
                           color='Clasificación',
                           color_discrete_map={'Óptima': '#2E7D32', 'Sobre': '#D32F2F', 'Sub': '#1976D2'},
                           hole=0.4)
        st.plotly_chart(fig_donut, use_container_width=True)

# --- TAB 2: MOTOR ---
with tab_motor:
    st.subheader("Desempeño Operativo por Motor")
    
    # Clean 'Motor' data if needed (remove 'Total' if present in rows, user said 'Total' is a value in Motor col)
    df_motor_clean = df_calidad[df_calidad['Motor'] != 'Total']
    
    # 1. Stacked Bar 100% by Motor (Quality)
    motor_group = df_motor_clean.groupby(['Motor', 'Clasificación'])['Valor'].sum().reset_index()
    # normalize to %
    motor_total = motor_group.groupby('Motor')['Valor'].transform('sum')
    motor_group['Pct'] = motor_group['Valor'] / motor_total * 100
    
    fig_motor = px.bar(motor_group, x='Pct', y='Motor', color='Clasificación',
                       title="Calidad de Aplicación por Motor (%)",
                       orientation='h',
                       text_auto='.1f',
                       color_discrete_map={'Óptima': '#2E7D32', 'Sobre': '#D32F2F', 'Sub': '#1976D2'})
    st.plotly_chart(fig_motor, use_container_width=True)
    
    # 2. Ranking Sobre-aplicacion
    top_sobre = motor_group[motor_group['Clasificación'] == 'Sobre'].sort_values('Pct', ascending=True)
    fig_sobre = px.bar(top_sobre, x='Pct', y='Motor', 
                       title="Ranking de Sobre-Aplicación (%)",
                       orientation='h',
                       color_discrete_sequence=['#D32F2F'])
    st.plotly_chart(fig_sobre, use_container_width=True)

# --- TAB 3: VELOCIDAD ---
with tab_speed:
    st.subheader("Impacto de la Velocidad en la Calidad")
    # Needed: Rows where type is 'Velocidad' or relate Speed to Quality.
    # User said: "Comportamiento por velocidad... Velocidad baja, Velocidad óptima, Velocidad alta"
    # Is there a column 'Velocidad' or is it in 'Clasificación' when 'Tipo' == 'Velocidad'?
    # Let's inspect 'Tipo'.
    
    df_speed = df_main[df_main['Tipo'] == 'Velocidad']
    # If Tipo is Velocidad, Clasification is likely Low, Opt, High?
    # Let's assume so based on description.
    
    if not df_speed.empty:
        speed_group = df_speed.groupby(['Clasificación'])['Valor'].sum().reset_index()
        fig_speed = px.bar(speed_group, x='Clasificación', y='Valor',
                           title="Área trabajada por rango de velocidad",
                           color='Clasificación',
                           color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_speed, use_container_width=True)
        
        st.info("Nota: Para correlacionar velocidad con calidad, se requiere una estructura de datos que cruce ambas variables a nivel de evento, o asumir que la proporción de velocidad en una suerte explica su calidad.")
    else:
        st.warning("No se encontraron datos específicos de Velocidad en la selección actual.")

# --- TAB 4: TERRITORIO ---
with tab_geo:
    st.subheader("Detalle por Hacienda y Suerte")
    
    # Aggregates per Suerte
    df_suerte_agg = df_calidad.groupby(['Zona', 'Hacienda', 'Suerte', 'Clasificación'])['Valor'].sum().unstack(fill_value=0).reset_index()
    
    # Add columns if missing
    for col in ['Óptima', 'Sobre', 'Sub']:
        if col not in df_suerte_agg.columns:
            df_suerte_agg[col] = 0
            
    df_suerte_agg['Total'] = df_suerte_agg['Óptima'] + df_suerte_agg['Sobre'] + df_suerte_agg['Sub']
    df_suerte_agg['% Óptima'] = (df_suerte_agg['Óptima'] / df_suerte_agg['Total'] * 100).round(1)
    df_suerte_agg['% Sobre'] = (df_suerte_agg['Sobre'] / df_suerte_agg['Total'] * 100).round(1)
    
    # View datatable
    st.dataframe(
        df_suerte_agg.sort_values('% Óptima', ascending=True),
        column_order=['Zona', 'Hacienda', 'Suerte', 'Total', '% Óptima', '% Sobre'],
        hide_index=True,
        use_container_width=True
    )
