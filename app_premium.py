import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_float import *
from chat_assistant import generate_data_context, query_openai
from query_engine import query_local
import calendar
import base64
from supabase import create_client

def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

logo_base64 = get_base64_image("logo_ipsa.JPG")

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Providencia FertiCal App",
    page_icon="logo_ipsa.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME COLORS ---
COLOR_PRIMARY = "#1B4332" # Deep Providencia Green
COLOR_ACCENT = "#D4AF37"  # Gold Accent
COLOR_BG = "#EDF5F1"      # Professional Light Green Canvas
COLOR_CARD = "#FFFFFF"
COLOR_SIDEBAR = "#FFFFFF"
COLOR_TEXT_MAIN = "#1A1C1E"
COLOR_TEXT_SEC = "#44474E"

# --- CUSTOM CSS ---
st.markdown(f"""
<style>
    /* Global Settings */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {COLOR_TEXT_MAIN};
        background-color: {COLOR_BG};
    }}

    h1, h2, h3, .kpi-value {{
        font-family: 'Outfit', sans-serif;
    }}
    
    /* Header Cleaning - Avoid hiding global buttons */
    header[data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }}
    
    /* KPI Cards - Glassmorphism style */
    .kpi-card {{
        background-color: {COLOR_CARD};
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(27, 67, 50, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .kpi-card::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, {COLOR_PRIMARY}, {COLOR_ACCENT});
        opacity: 0.8;
    }}
    .kpi-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: {COLOR_PRIMARY};
    }}
    .kpi-label {{
        color: {COLOR_TEXT_SEC};
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .kpi-value {{
        color: {COLOR_PRIMARY};
        font-size: 2.25rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }}
    .kpi-sub {{
        font-size: 0.8rem;
        color: {COLOR_TEXT_SEC};
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;
    }}
    
    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1.5rem;
        background-color: transparent;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }}
    .stTabs [data-baseweb="tab"] {{
        height: auto;
        padding: 0.75rem 1.5rem;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: {COLOR_TEXT_SEC};
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {COLOR_PRIMARY};
        background-color: rgba(27, 67, 50, 0.03);
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: {COLOR_PRIMARY};
        border-bottom: 3px solid {COLOR_PRIMARY};
        background-color: rgba(27, 67, 50, 0.05);
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: {COLOR_SIDEBAR};
        border-right: 1px solid rgba(0,0,0,0.08);
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 2rem !important;
    }}
    
    /* Input Styling for technology feel */
    .stSelectbox label, .stMultiSelect label, .stSlider label {{
        color: {COLOR_PRIMARY} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }}
    div[data-baseweb="select"] {{
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid rgba(27, 67, 50, 0.1) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }}
    div[data-testid="stExpander"] {{
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        background-color: white !important;
    }}

    /* Header Banner */
    .header-banner {{
        background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, #2D6A4F 100%);
        padding: 2rem 3rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 2.5rem;
        box-shadow: 0 10px 25px rgba(27, 67, 50, 0.12);
        position: relative;
        overflow: hidden;
    }}
    .header-logo-container {{
        background: white;
        padding: 12px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        flex-shrink: 0;
    }}
    .header-logo {{
        width: 100px;
        height: auto;
    }}
    .header-banner::after {{
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }}
    .header-text-container {{
        text-align: left;
    }}
    .header-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }}
    .header-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.75rem;
        font-weight: 400;
        max-width: 800px;
    }}
    
    /* Narrative Summary Style */
    .narrative-box {{
        background: white;
        padding: 2rem;
        border-radius: 20px;
        border-left: 8px solid {COLOR_PRIMARY};
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }}
    .narrative-title {{
        color: {COLOR_PRIMARY};
        font-family: 'Outfit';
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .narrative-text {{
        font-size: 1.05rem;
        line-height: 1.6;
        color: {COLOR_TEXT_MAIN};
    }}
    .highlight-val {{
        color: {COLOR_PRIMARY};
        font-weight: 700;
        background: rgba(27, 67, 50, 0.05);
        padding: 2px 6px;
        border-radius: 4px;
    }}
    
    /* Chat Widget Styles - Improved with Animation */
    .chat-button {{
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 65px;
        height: 65px;
        border-radius: 50%;
        background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_ACCENT} 100%);
        box-shadow: 0 8px 16px rgba(27, 67, 50, 0.3);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: pulse-green 2s infinite;
    }}
    
    @keyframes pulse-green {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 125, 50, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 15px rgba(46, 125, 50, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 125, 50, 0); }}
    }}

    .chat-button:hover {{
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 12px 20px rgba(27, 67, 50, 0.4);
        animation: none;
    }}

    /* Message bubble visibility fix */
    .stChatMessage {{ padding: 10px !important; }}

    /* Mobile Responsiveness */
    @media (max-width: 768px) {{
        .header-banner {{
            flex-direction: column !important;
            padding: 1.5rem !important;
            text-align: center !important;
            gap: 1.5rem !important;
        }}
        .header-text-container {{
            text-align: center !important;
        }}
        .header-title {{
            font-size: 1.8rem !important;
        }}
        .header-subtitle {{
            font-size: 1rem !important;
        }}
        .kpi-card {{
            padding: 15px !important;
            margin-bottom: 10px !important;
        }}
        .kpi-value {{
            font-size: 1.5rem !important;
        }}
        .narrative-box {{
            padding: 1.25rem !important;
        }}
        .summary-ribbon {{
            flex-direction: column !important;
            gap: 10px !important;
            align-items: flex-start !important;
        }}
        .ribbon-group {{
            width: 100% !important;
            justify-content: space-between !important;
            flex-wrap: wrap !important;
        }}
        
        /* Floating container adjustments (handled via the float call now) */
    }}
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data(ttl=3600)  # Cache for 1 hour to optimize performance
def load_data():
    try:
        # Load credentials (Streamlit features st.secrets for cloud deployment)
        if "SUPABASE_URL" in getattr(st, "secrets", {}) and "SUPABASE_ANON_KEY" in getattr(st, "secrets", {}):
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_ANON_KEY"]
        else:
            # Fallback to local config file for development
            try:
                from supabase_config import SUPABASE_URL, SUPABASE_ANON_KEY
                url = SUPABASE_URL
                key = SUPABASE_ANON_KEY
            except ImportError:
                st.error("No se encontraron credenciales de Supabase (requeridas en st.secrets o supabase_config.py)")
                return pd.DataFrame()

        # Initializing Supabase client
        supabase = create_client(url, key)
        
        # Paginated fetch to work around the 1000 row limit of Supabase API
        data = []
        count_response = supabase.table('fertilization_data').select('*', count='exact').execute()
        count = count_response.count if count_response.count else 0
        
        if count > 0:
            limit = 1000
            for i in range(0, count, limit):
                response = supabase.table('fertilization_data').select('*').range(i, i + limit - 1).execute()
                data.extend(response.data)

            df = pd.DataFrame(data)
            
            # Map database columns back to what the app expects
            df = df.rename(columns={
                'fecha_labor': 'Fecha_Labor',
                'año': 'Año',
                'mes': 'Mes',
                'zona': 'Zona',
                'hacienda': 'Hacienda',
                'hac_ste': 'Hac_ste',
                'suerte': 'Suerte',
                'motor': 'Motor',
                'tipo': 'Tipo',
                'metrica': 'Métrica',
                'clasificacion': 'Clasificación',
                'valor': 'Valor',
                'area_ste': 'Area_ste',
                'area_aplicada': 'Area_aplicada',
                'fecha_recomendacion': 'Fecha_Recomendacion',
                'unidades': 'Unidades'
            })
            
            if not df.empty:
                df['Fecha_Labor'] = pd.to_datetime(df['Fecha_Labor'])
                df['Motor'] = df['Motor'].fillna('Desconocido')
                return df

    except Exception as e:
        st.error(f"⚠️ Error crítico conectando a Supabase: {e}")
        
    return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("⚠️ El dataset está vacío o no se pudo cargar. Revisa la base de datos o ruta del archivo.")
    st.stop()

# st.write(f"Debug: Loaded {len(df)} rows") # Uncomment for debug

# --- CHAT ASSISTANT SETUP ---
OPENAI_API_KEY = getattr(st, "secrets", {}).get("OPENAI_API_KEY", "")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "¡Hola! 👋 Soy *Sam IA*, tu asistente de agricultura de precisión. Estoy aquí para ayudarte a analizar los datos de fertilización. ¿En qué puedo ayudarte hoy? 🌾"}
    ]
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False


# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.image("logo_ipsa.JPG", width=200)
    st.markdown(f"<h3 style='color: {COLOR_PRIMARY}; text-align: center;'>Configuración Operativa</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Selection
    all_years = sorted(df['Año'].dropna().unique())
    selected_year = st.selectbox("📅 Año de Cosecha", ["Todos"] + list(all_years))
    
    if selected_year != "Todos":
        df = df[df['Año'] == selected_year]
        
    all_months = sorted(df['Mes'].dropna().unique())
    selected_months = st.multiselect("📆 Periodo Mensual", all_months, default=[])
    if selected_months:
        df = df[df['Mes'].isin(selected_months)]
        
    # Zone
    all_zones = sorted(df['Zona'].dropna().unique())
    selected_zones = st.multiselect("🌍 Zonas Operativas", all_zones)
    if selected_zones:
        df = df[df['Zona'].isin(selected_zones)]
        
    # Hacienda
    all_haciendas = sorted(df['Hacienda'].dropna().unique())
    selected_haciendas = st.multiselect("🏠 Haciendas", all_haciendas)
    if selected_haciendas:
        df = df[df['Hacienda'].isin(selected_haciendas)]
        
    # Suerte (Searchable)
    all_suertes = sorted(df['Suerte'].astype(str).unique())
    selected_suertes = st.multiselect("📍 Buscar Suerte", all_suertes)
    if selected_suertes:
        df = df[df['Suerte'].astype(str).isin(selected_suertes)]

    # Motor
    all_motores = sorted(df['Motor'].dropna().unique())
    selected_motores = st.multiselect("🚜 Equipos y Motores", all_motores)
    if selected_motores:
        df = df[df['Motor'].isin(selected_motores)]
        
    st.markdown("---")
    st.caption(f"Registros filtrados: {len(df):,}")
    
    if st.button("Limpiar Filtros", type="primary"):
        st.session_state.clear()
        st.rerun()

# --- KPI METRICS LOGIC ---
valid_classifs = ['Sobre', 'Sub', 'Óptima']
# Check exact string match for 'Area' vs 'Área'
df_area = df[df['Métrica'].isin(['Area', 'Área'])] 
df_quality = df_area[df_area['Clasificación'].isin(valid_classifs)]

# KPI Global Calculation: Use only 'Total' motor to avoid duplication/double counting
# User feedback: "no sumar todas las areas de los motores porque hay duplicidad"
# We assume 'Total' rows represent the consolidated unique area per Suerte/Date.
df_kpis = df_quality[df_quality['Motor'] == 'Total']

total_area = df_kpis['Valor'].sum()
optima_val = df_kpis[df_kpis['Clasificación'] == 'Óptima']['Valor'].sum()
sobre_val = df_kpis[df_kpis['Clasificación'] == 'Sobre']['Valor'].sum()
sub_val = df_kpis[df_kpis['Clasificación'] == 'Sub']['Valor'].sum()

# Percentages
pct_opt = (optima_val / total_area * 100) if total_area else 0
pct_sobre = (sobre_val / total_area * 100) if total_area else 0
pct_sub = (sub_val / total_area * 100) if total_area else 0

# --- GLOBAL INSIGHT CALCULATIONS (Fixing NameError) ---
df_m_stats = df_quality[~df_quality['Motor'].isin(['Total', 'No aplica'])]
if not df_m_stats.empty:
    m_metrics = df_m_stats.groupby(['Motor', 'Clasificación'])['Valor'].sum().unstack(fill_value=0)
    # Ensure columns exist
    for c in ['Sobre', 'Óptima', 'Sub']:
        if c not in m_metrics.columns: m_metrics[c] = 0
    m_metrics['Total_M'] = m_metrics.sum(axis=1)
    m_metrics['Pct_Sobre'] = (m_metrics['Sobre'] / m_metrics['Total_M'] * 100).fillna(0)
    worst_motor = m_metrics['Pct_Sobre'].idxmax()
    worst_val = m_metrics['Pct_Sobre'].max()
else:
    worst_motor = "N/A"
    worst_val = 0

# Cobertura logic (Simplified approximation based on available columns)
# Need unique (Suerte, Fecha) to sum Area_ste properly without duplication from atomic rows
unique_evts = df[['Hacienda', 'Suerte', 'Fecha_Labor', 'Area_ste', 'Area_aplicada']].drop_duplicates()
total_ste = unique_evts['Area_ste'].sum()
total_app = unique_evts['Area_aplicada'].sum()
pct_cobertura = (total_app / total_ste * 100) if total_ste else 0

# --- HELPER FUNCTIONS ---
def apply_premium_layout(fig, title=None):
    fig.update_layout(
        title={
            'text': title,
            'font': {'family': 'Outfit, sans-serif', 'size': 20, 'color': COLOR_PRIMARY},
            'x': 0.05,
            'xanchor': 'left'
        } if title else None,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Inter, sans-serif",
        font_color=COLOR_TEXT_SEC,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.05)",
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Inter, sans-serif",
            bordercolor="rgba(0,0,0,0.1)"
        )
    )
    fig.update_xaxes(showgrid=False, linecolor="rgba(0,0,0,0.1)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False)
    return fig


def format_selection(value):
    if not value:
        return "Todas"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)

year_txt = selected_year
month_txt = format_selection(selected_months)
zone_txt = format_selection(selected_zones)
hacienda_txt = format_selection(selected_haciendas)


# --- HEADER BANNER ---
st.markdown(f"""
<div class="header-banner">
    <div class="header-logo-container">
        <img src="data:image/jpeg;base64,{logo_base64}" class="header-logo">
    </div>
    <div class="header-text-container">
        <h1 class="header-title">Providencia FertiCal App</h1>
        <p class="header-subtitle">Inteligencia de Datos Aplicada al Análisis de Calidad de la Fertilización</p>
        <div style="margin-top: 0.5rem; opacity: 0.8; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase;">
            Analizando: Año {year_txt}, Mes {month_txt}, Zona {zone_txt}, Hacienda {hacienda_txt}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- NARRATIVE SUMMARY ---
st.markdown(f"""
<div class="narrative-box">
    <div class="narrative-title">📖 Resumen Ejecutivo de Operación</div>
    <div class="narrative-text">
        Durante el periodo seleccionado, se ha gestionado una superficie total de <span class="highlight-val">{total_area:,.0f} hectáreas</span>. 
        El desempeño operativo muestra una <span class="highlight-val">Calidad Óptima del {pct_opt:.1f}%</span>, lo cual indica un nivel de cumplimiento 
        {'superior al estándar' if pct_opt > 85 else 'con oportunidades de mejora'} de Providencia. 
        Se detectó una sobre-aplicación en el <span class="highlight-val">{pct_sobre:.1f}%</span> del área, lo que representa un impacto directo en el uso de insumos, 
        mientras que un <span class="highlight-val">{pct_sub:.1f}%</span> del territorio se encuentra bajo el umbral de fertilización requerida (Sub-aplicación).
    </div>
</div>
""", unsafe_allow_html=True)

# --- KPI CARDS (HTML) ---
def kpi_card(label, value, sub_label, trend_val, is_good_trend=True, icon="📊"):
    trend_cls = "trend-up" if is_good_trend else "trend-down" # Simplification
    # Logic for trend color: if value is good (high optima), green. If value is bad (high sobre), red.
    
    # We'll use the sub_label to show target/context
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">
            {sub_label}
        </div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    kpi_card("Área Total", f"{total_area:,.0f} ha", "Superficie fertilizada procesada", "", icon="🌾")
with col2:
    status = "✅" if pct_opt >= 85 else "⚠️"
    kpi_card("Calidad Óptima", f"{pct_opt:.1f}%", f"<span class='trend-{'up' if pct_opt>=85 else 'down'}'>Meta: >85%</span>", "", icon=status)
with col3:
    status = "🛑" if pct_sobre > 5 else "✅"
    kpi_card("Sobre-aplicación", f"{pct_sobre:.1f}%", f"<span class='trend-{'down' if pct_sobre>5 else 'up'}'>Desperdicio</span>", "", icon=status, is_good_trend=False)
with col4:
    kpi_card("Sub-aplicación", f"{pct_sub:.1f}%", "Riesgo productivo", "", icon="📉")
with col5:
    kpi_card("Cobertura", f"{pct_cobertura:.1f}%", "Sobre área programada", "", icon="🎯")

st.markdown("---")

# --- NARRATIVE TABS ---
tab_calidad, tab_geo = st.tabs(["📊 Evolución y Desempeño", "🗺️ Detalle por suertes"])

with tab_calidad:
    st.subheader("📈 Análisis de Evolución y Distribución por Zonas")
    
    # ROW 1: Evolution and Global Distribution
    r1_c1, r1_c2 = st.columns([2, 1])
    
    with r1_c1:
        # Time Series
        df_time = df_kpis.copy()
        df_time['Mes_Num'] = df_time['Fecha_Labor'].dt.month
        grouped_time = df_time.groupby(['Mes_Num', 'Clasificación'])['Valor'].sum().reset_index()
        import calendar
        grouped_time['Mes'] = grouped_time['Mes_Num'].apply(lambda x: calendar.month_name[x])
        
        fig_time = px.bar(grouped_time, x='Mes', y='Valor', color='Clasificación',
                          color_discrete_map={'Óptima': COLOR_PRIMARY, 'Sobre': '#EF5350', 'Sub': '#42A5F5'},
                          barmode='stack', text_auto='.1s')
        apply_premium_layout(fig_time, "Evolución Mensual de Calidad (ha)")
        st.plotly_chart(fig_time, use_container_width=True)
        
    with r1_c2:
        # Donut Distribution
        grouped_dist = df_kpis.groupby('Clasificación')['Valor'].sum().reset_index()
        fig_dist = px.pie(grouped_dist, values='Valor', names='Clasificación',
                          color='Clasificación',
                          color_discrete_map={'Óptima': COLOR_PRIMARY, 'Sobre': '#EF5350', 'Sub': '#42A5F5'},
                          hole=0.65)
        apply_premium_layout(fig_dist, "Distribución Global")
        fig_dist.update_traces(textposition='inside', textinfo='percent')
        fig_dist.update_layout(showlegend=True, legend=dict(yanchor="bottom", y=-0.1, xanchor="center", x=0.5, orientation="h"))
        st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ROW 2: Zone Distribution and Insights
    r2_c1, r2_c2 = st.columns([2, 1.2])
    
    with r2_c1:
        # Zone Distribution
        df_zone_qual = df_kpis.groupby(['Zona', 'Clasificación'])['Valor'].sum().reset_index()
        totals_z = df_zone_qual.groupby('Zona')['Valor'].transform('sum')
        df_zone_qual['Pct'] = (df_zone_qual['Valor'] / totals_z * 100)
        
        fig_zone = px.bar(df_zone_qual, y='Zona', x='Pct', color='Clasificación',
                          orientation='h', text_auto='.1f',
                          color_discrete_map={'Óptima': COLOR_PRIMARY, 'Sobre': '#EF5350', 'Sub': '#42A5F5'})
        apply_premium_layout(fig_zone, "Distribución de Calidad por Zona (%)")
        st.plotly_chart(fig_zone, use_container_width=True)

    with r2_c2:
        # Smart Insights Card
        st.markdown(f"""
        <div style="background-color: #FFFFFF; padding: 24px; border-radius: 20px; border-left: 10px solid {COLOR_PRIMARY}; box-shadow: 0 10px 25px rgba(0,0,0,0.05); height: 100%;">
            <h3 style="margin:0; color: {COLOR_PRIMARY}; font-family: 'Outfit'; font-size: 1.6rem;">💡 Insights clave de calidad</h3>
            <p style="color: {COLOR_TEXT_SEC}; font-size: 1rem; margin-top: 15px; line-height: 1.6;">
                Actualmente, el sistema identifica que la calidad <b>Óptima</b> global es del <b>{pct_opt:.1f}%</b>.
            </p>
            <hr style="opacity: 0.1; margin: 15px 0;">
            <ul style="margin: 0; padding-left: 20px; font-size: 0.95rem; color: {COLOR_TEXT_SEC}; line-height: 1.8;">
                <li>El motor con mayor desvío es <b style="color: #EF5350;">{worst_motor}</b> ({worst_val:.1f}% sobre-aplicación).</li>
                <li>Se han procesado <b>{total_area:,.0f} ha</b> en el periodo.</li>
                <li>El desperdicio estimado por sobre-aplicación es de <b style="color: #EF5350;">{sobre_val:,.1f} ha</b>.</li>
                <li>La zona con mayor oportunidad de mejora se visualiza en el gráfico adyacente.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.subheader("🚜 Análisis calidad de motores ")
    
    # ROW 3: Engine Ranking and Engine by Zone
    r3_c1, r3_c2 = st.columns(2)
    
    with r3_c1:
        # Engine Ranking (Moved from Tab 2)
        df_m = df_quality[~df_quality['Motor'].isin(['No aplica'])]
        motor_group = df_m.groupby(['Motor', 'Clasificación'])['Valor'].sum().reset_index()
        totals_m = motor_group.groupby('Motor')['Valor'].transform('sum')
        motor_group['Pct'] = (motor_group['Valor'] / totals_m * 100)
        motor_order = motor_group[motor_group['Clasificación'] == 'Sobre'].sort_values('Pct', ascending=True)['Motor'].tolist()
        
        fig_motor = px.bar(motor_group, y='Motor', x='Pct', color='Clasificación',
                           orientation='h', text_auto='.1f',
                           category_orders={'Motor': motor_order},
                           color_discrete_map={'Óptima': COLOR_PRIMARY, 'Sobre': '#EF5350', 'Sub': '#42A5F5'})
        apply_premium_layout(fig_motor, "Ranking de Desempeño Operativo (%)")
        fig_motor.update_xaxes(title="% del Área", range=[0, 100])
        st.plotly_chart(fig_motor, use_container_width=True)

    with r3_c2:
        # Fixed to 'Óptima' as requested by user
        metric_choice = "Óptima"
        
        # We show the % for each motor across zones based on selection
        df_mz = df_quality[~df_quality['Motor'].isin(['Total', 'No aplica'])]
        df_mz_grouped = df_mz.groupby(['Zona', 'Motor', 'Clasificación'])['Valor'].sum().unstack(fill_value=0).reset_index()
        
        # Ensure all possible columns exist
        for c in ["Óptima", "Sobre", "Sub"]:
            if c not in df_mz_grouped.columns: df_mz_grouped[c] = 0
            
        df_mz_grouped['Total'] = df_mz_grouped[["Óptima", "Sobre", "Sub"]].sum(axis=1)
        df_mz_grouped['% Metric'] = (df_mz_grouped[metric_choice] / df_mz_grouped['Total'] * 100).fillna(0)
        
        # Pivot for heatmap
        pivot_mz = df_mz_grouped.pivot(index='Motor', columns='Zona', values='% Metric').fillna(0)
        
        # Enhanced Color scale: Sequential with sharp break at 85%
        # Using a slightly softer red and a premium deep green
        c_scale = [
            [0.0, '#FFEBEE'],    # Very light red (for 0%)
            [0.849, '#EF5350'],  # Strong red at the edge
            [0.85, '#2D664F'],   # Premium Green starts here
            [1.0, '#1B4332']     # Deep Forest Green
        ]
        
        title_mz = f"Matriz de Inteligencia: % {metric_choice} por Zona"
        fig_mz = px.imshow(pivot_mz, 
                           text_auto='.1f', 
                           aspect="auto",
                           color_continuous_scale=c_scale,
                           zmin=0, zmax=100,
                           labels=dict(x="Zona", y="Motor", color=f"% {metric_choice}"))
        
        apply_premium_layout(fig_mz, title_mz)
        fig_mz.update_layout(
            coloraxis_showscale=True,
            coloraxis_colorbar=dict(
                title="%",
                thicknessmode="pixels", thickness=15,
                lenmode="fraction", len=0.8,
                yanchor="middle", y=0.5,
                ticks="outside"
            ),
            margin=dict(l=50, r=20, t=80, b=50)
        )
        # Adding gaps between cells for a modern 'grid' feel
        fig_mz.update_traces(xgap=3, ygap=3)
        st.plotly_chart(fig_mz, use_container_width=True)



with tab_geo:
    # --- DATA PREPARATION ---
    # Use df_kpis (Total Motor only) to ensure we are showing the true state of the Suerte, not sum of motors
    if not df_kpis.empty:
        pivot_geo = df_kpis.groupby(['Zona', 'Hacienda', 'Suerte', 'Clasificación'])['Valor'].sum().unstack(fill_value=0).reset_index()
        
        if 'Fecha_Recomendacion' in df.columns and 'Unidades' in df.columns:
            suerte_info = df.groupby(['Zona', 'Hacienda', 'Suerte']).agg({
                'Fecha_Recomendacion': 'first',
                'Unidades': 'first'
            }).reset_index()
            pivot_geo = pd.merge(pivot_geo, suerte_info, on=['Zona', 'Hacienda', 'Suerte'], how='left')
            pivot_geo['Fecha_Recomendacion'] = pd.to_datetime(pivot_geo['Fecha_Recomendacion'], errors='coerce').dt.date
        else:
            pivot_geo['Fecha_Recomendacion'] = None
            pivot_geo['Unidades'] = 0

        # Ensure all columns exist
        for col in ['Óptima', 'Sobre', 'Sub']:
            if col not in pivot_geo.columns:
                pivot_geo[col] = 0
                
        pivot_geo['Total App'] = pivot_geo['Óptima'] + pivot_geo['Sobre'] + pivot_geo['Sub']
        pivot_geo['% Óptima'] = (pivot_geo['Óptima'] / pivot_geo['Total App'] * 100).fillna(0).round(1)
        pivot_geo['% Sobre'] = (pivot_geo['Sobre'] / pivot_geo['Total App'] * 100).fillna(0).round(1)
        pivot_geo['% Sub'] = (pivot_geo['Sub'] / pivot_geo['Total App'] * 100).fillna(0).round(1)
        
        # Calculate summary statistics BEFORE reindexing (which drops columns)
        num_lotes = len(pivot_geo)
        area_total_sum = pivot_geo['Total App'].sum()
        area_opt_sum = pivot_geo['Óptima'].sum()
        area_sobre_sum = pivot_geo['Sobre'].sum()
        area_sub_sum = pivot_geo['Sub'].sum()
        unidades_promedio = pivot_geo['Unidades'].mean()    

        # Reorder columns explicitly BEFORE styling to ensure consistency
        display_cols = ['Zona', 'Hacienda', 'Suerte', 'Fecha_Recomendacion', 'Unidades', 'Total App', '% Óptima', '% Sobre', '% Sub']
        pivot_geo = pivot_geo.reindex(columns=display_cols, fill_value=0)

        st.subheader("🌐 Indicadores principales de gestión")

        # --- TERRITORIAL LOGIC (Defensive) --- 
        zone_metrics = pivot_geo.groupby('Zona').agg({
            'Total App': 'sum',
            '% Óptima': 'mean',
            '% Sobre': 'mean'
        }).reset_index() if not pivot_geo.empty else pd.DataFrame()
        
        if not zone_metrics.empty:
            best_zone = zone_metrics.loc[zone_metrics['% Óptima'].idxmax()]
            worst_zone = zone_metrics.loc[zone_metrics['% Sobre'].idxmax()]
            
            # Critical Suertes (Outliers) - Updated to >15% deviation (Sobre or Sub)
            critical_suertes = pivot_geo[(pivot_geo['% Sobre'] > 15) | (pivot_geo['% Sub'] > 15)]
            num_critical = len(critical_suertes)
            
            # Top Hacienda
            hacienda_metrics = pivot_geo.groupby('Hacienda')['% Óptima'].mean().reset_index()
            top_hacienda = hacienda_metrics.loc[hacienda_metrics['% Óptima'].idxmax()]

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                kpi_card("Área Total", f"{total_area:,.0f} ha", "Superficie fertilizada procesada", "", icon="🌾")
            with col5:
                kpi_card("Suertes", f"{num_lotes:,.0f}", "Numero de suertes evaludas", "", icon="📊")
            with col2:            
                kpi_card("Área Optima", f"{area_opt_sum:,.0f} ha", "Área superior al 85%","", icon="✅") 
            with col3:
                kpi_card("Área Sobre Aplicada", f"{area_sobre_sum:,.0f} ha", "Sobre costo y desperdicio", "", icon="⚠️")
            with col4:
                kpi_card("Área Sub Aplicada", f"{area_sub_sum:,.0f} ha", "Influencia en el desarrollo", "", icon="📉")

            st.markdown("---")

            # --- SUMMARY RIBBON (CLEAN & SUBTLE) ---
            #st.markdown(f"""
            #<div class="summary-ribbon" style="background: rgba(27, 67, 50, 0.03); padding: 12px 20px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
             #   <div class="ribbon-group" style="display: flex; gap: 25px;">
              #      <span style="font-size: 0.9rem; color: {COLOR_TEXT_SEC};">📍 <b>{num_lotes}</b> Suertes</span>
               #     <span style="font-size: 0.9rem; color: {COLOR_TEXT_SEC};">📐 Total: <b>{area_total_sum:,.1f} ha</b></span>
                #</div>
                #<div class="ribbon-group" style="display: flex; gap: 15px;">
                 #   <span style="font-size: 0.85rem; color: #2E7D32; background: #E8F5E9; padding: 2px 10px; border-radius: 20px;">✅ Óptima: {area_opt_sum:,.1f} ha</span>
                  #  <span style="font-size: 0.85rem; color: #C62828; background: #FFEBEE; padding: 2px 10px; border-radius: 20px;">⚠️ Sobre: {area_sobre_sum:,.1f} ha</span>
                   # <span style="font-size: 0.85rem; color: #1565C0; background: #E3F2FD; padding: 2px 10px; border-radius: 20px;">📉 Sub: {area_sub_sum:,.1f} ha</span>
                #</div>
            #</div>
            #""", unsafe_allow_html=True)


            st.subheader("📊 Analisis detallado")
            # --- INSIGHT PANEL ---
            i1, i2, i3, i4, i5 = st.columns(5)
            
            with i1:
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 12px; border-top: 4px solid {COLOR_PRIMARY}; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">🌟 Zona Líder</p>
                    <h4 style="color: {COLOR_PRIMARY}; margin: 0; font-size: 1.1rem;">{best_zone['Zona']}</h4>
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.8rem; margin-top: 0.25rem;">Eficiencia: <b>{best_zone['% Óptima']:.1f}%</b></p>
                </div>
                """, unsafe_allow_html=True)

            with i2:
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 12px; border-top: 4px solid #EF5350; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">⚠️ Zona Crítica</p>
                    <h4 style="color: #EF5350; margin: 0; font-size: 1.1rem;">{worst_zone['Zona']}</h4>
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.8rem; margin-top: 0.25rem;">Sobre-Dosis: <b>{worst_zone['% Sobre']:.1f}%</b></p>
                </div>
                """, unsafe_allow_html=True)

            with i3:
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 12px; border-top: 4px solid {COLOR_ACCENT}; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">🏆 Hacienda Top</p>
                    <h4 style="color: {COLOR_TEXT_MAIN}; margin: 0; font-size: 1.1rem;">{top_hacienda['Hacienda']}</h4>
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.8rem; margin-top: 0.25rem;">Calidad: <b>{top_hacienda['% Óptima']:.1f}%</b></p>
                </div>
                """, unsafe_allow_html=True)

            with i4:
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 12px; border-top: 4px solid #FFA726; box-shadow: 0 4px 6px rgba(0,0,0,0.05); position: relative;">
                    <div style="position: absolute; top: 5px; right: 5px; cursor: help; font-size: 0.8rem;" title="Alerta: Desviaciones (Sobre/Sub) > 15%">ℹ️</div>
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">🚩 Alertas de Lote</p>
                    <h4 style="color: #E65100; margin: 0; font-size: 1.1rem;">{num_critical} Suertes</h4>
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.8rem; margin-top: 0.25rem;">Desviaciones >15%</p>
                </div>
                """, unsafe_allow_html=True)

            with i5:
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 12px; border-top: 4px solid #FFA726; box-shadow: 0 4px 6px rgba(0,0,0,0.05); position: relative;">
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">Unidades promedio</p>
                    <h4 style="color: #E65100; margin: 0; font-size: 1.1rem;">{unidades_promedio:.1f}</h4>
                    <p style="color: {COLOR_TEXT_SEC}; font-size: 0.8rem; margin-top: 0.25rem;">Unidades recomendadas promedio</p>
                </div>
                """, unsafe_allow_html=True)



        # Manual Sorting
        c_sort, c_blank = st.columns([1, 4])
        with c_sort:
            sort_by = st.selectbox("Ordenar desempeño por:", ["% Sobre", "% Sub", "% Óptima", "Total App"])
       
        # Sort by user selection
        pivot_geo = pivot_geo.sort_values(sort_by, ascending=False)
        
        # Table
        st.dataframe(
            pivot_geo,
            column_order=['Zona', 'Hacienda', 'Suerte','Fecha_Labor','Fecha_Recomendacion', 'Unidades', 'Total App', '% Óptima', '% Sobre', '% Sub'],
            column_config={
                "Fecha_Labor": st.column_config.DateColumn("Fecha Labor", format="DD/MM/YYYY"),
                "Fecha_Recomendacion": st.column_config.DateColumn("Fecha Recomendación", format="DD/MM/YYYY"),
                "Unidades": st.column_config.NumberColumn("Unidades Recomendadas", format="%.1f"),
                "Total App": st.column_config.NumberColumn("Área (ha)", format="%.1f ha"),
                "% Óptima": st.column_config.ProgressColumn("Calidad Óptima", format="%.1f%%", min_value=0, max_value=100),
                "% Sobre": st.column_config.ProgressColumn("Sobre-Dosis", format="%.1f%%", min_value=0, max_value=100),
                "% Sub": st.column_config.ProgressColumn("Sub-Dosis", format="%.1f%%", min_value=0, max_value=100),
            },
            use_container_width=True,
            hide_index=True,
            height=600
        )
    else:
        st.info("No hay datos territoriales disponibles para los filtros seleccionados.")

# --- AI CHAT ASSISTANT (Floating Button) ---
float_init()

# Floating button with avatar
button_container = st.container()
with button_container:
    if st.button("🤖", key="float_chat_btn", help="Chatea con Sam IA"):
        st.session_state.chat_open = not st.session_state.chat_open

button_container.float("bottom: 2rem; right: 2rem; background: linear-gradient(135deg, #2E7D32 0%, #81C784 100%); border-radius: 50%; width: 70px; height: 70px; box-shadow: 0 4px 12px rgba(46, 125, 50, 0.4); display: flex; align-items: center; justify-content: center; font-size: 32px;")

# Chat panel with modern design
if st.session_state.chat_open:
    chat_container = st.container()
    with chat_container:
        # Header with avatar, title and action buttons
        col_header, col_actions = st.columns([3, 1])
        with col_header:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #2E7D32 0%, #81C784 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                    🤖
                </div>
                <div>
                    <h3 style="margin: 0; font-size: 18px; color: #1f2937;">Sam IA</h3>
                    <p style="margin: 0; font-size: 12px; color: #6b7280;">Chatea conmigo sobre tus datos de fertilización</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_actions:
            if st.button("🗑️", key="clear_chat", help="Limpiar chat"):
                st.session_state.chat_history = [
                    {"role": "assistant", "content": "¡Hola! 👋 Soy **Sam IA**, tu asistente de agricultura de precisión. Estoy aquí para ayudarte a analizar los datos de fertilización. ¿En qué puedo ayudarte hoy? 🌾"}
                ]
                st.rerun()
            if st.button("❌", key="close_chat", help="Cerrar chat"):
                st.session_state.chat_open = False
                st.rerun()
        
        st.markdown("---")
        
        # Chat messages with native Streamlit bubbles for Markdown support
        messages_container = st.container()
        with messages_container:
            for msg in st.session_state.chat_history:
                avatar = "🤖" if msg['role'] == 'assistant' else None
                with st.chat_message(msg['role'], avatar=avatar):
                    st.markdown(msg['content'])
        
        st.markdown("---")
        
        # Input area - using chat_input for better UX
        user_input = st.chat_input("Escribe tu mensaje...", key="chat_input_field")
        
        # Handle input submission
        if user_input:
            # Display user message in chat message container
            with messages_container:
                with st.chat_message("user"):
                    st.markdown(user_input)
            
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Show thinking indicator
            with messages_container:
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Sam IA está analizando los datos... 📊"):
                        # Try local query first (FREE!)
                        local_answer, used_local = query_local(user_input, df)
                        
                        if used_local:
                            response = local_answer
                        else:
                            # Complex question - use OpenAI
                            context = generate_data_context(df)
                            response = query_openai(user_input, context, OPENAI_API_KEY)
                        
                        st.markdown(response)
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    chat_container.float("bottom: 5rem; right: 5%; width: 90%; max-width: 400px; max-height: 75vh; background: white; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.15); padding: 1.25rem; overflow-y: auto;")


 