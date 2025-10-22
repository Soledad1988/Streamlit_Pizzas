import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ------------------ Configuración de la página ------------------
st.set_page_config(
    page_title="Call center",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------- Sidebar Title -------
# ------- Ocultar menú lateral predeterminado -------
hide_default_sidebar = """
    <style>
        /* Oculta la navegación de páginas automática */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* También oculta el contenedor del título predeterminado */
        [data-testid="stSidebarNavItems"] {
            display: none !important;
        }

        /* Asegura que tu propio menú quede arriba sin espacios vacíos */
        section[data-testid="stSidebar"] div:nth-child(1) {
            padding-top: 0 !important;
        }
    </style>
"""
st.markdown(hide_default_sidebar, unsafe_allow_html=True)

st.sidebar.markdown("### 📞 Centro de llamadas")

# ------- Opciones del menú -------
menu = ["Llamadas", "Agentes", "Temas"]
icons = ["📞", "👥", "📄"]
page_files = {
    "Llamadas": "llamadas.py",
    "Agentes": "pages/agentes.py",
    "Temas": "pages/temas.py" 
}

# Guardamos en la sesión la opción seleccionada
if "selected_page" not in st.session_state:
    st.session_state.selected_page = menu[0]

# Mostrar el menú visualmente
for i, item in enumerate(menu):
    is_active = item == st.session_state.selected_page
    active_class = "active" if is_active else ""
    if st.sidebar.button(f"{icons[i]} {item}", key=item):
        st.session_state.selected_page = item
        st.switch_page(page_files[item])  # ⬅ Cambio de página real

# ------- CSS para mejorar estilo -------
st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background-color: #F8F9FB;
    }
    .active {
        background-color: #DDE3EC;
        border-radius: 10px;
        font-weight: 600;
    }
    button[kind="secondary"] {
        width: 100%;
        text-align: left;
        background-color: transparent;
        border-radius: 10px;
    }
    button[kind="secondary"]:hover {
        background-color: #E9ECEF;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ Paleta minimalista ------------------
PALETTE = {
    "bg": "#FFFFFF",
    "text": "#2B2D42",      # dark slate
    "muted": "#7D8A99",    # gray
    "accent": "#D6457B",   # soft muted pink accent
    "card_bg": "#F8F9FB"   # very light gray card background
}

plt.rcParams.update({
    "figure.facecolor": PALETTE["bg"],
    "axes.facecolor": PALETTE["bg"],
    "axes.edgecolor": PALETTE["muted"],
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.labelcolor": PALETTE["text"],
    "xtick.color": PALETTE["muted"],
    "ytick.color": PALETTE["muted"],
    "font.size": 10,
})

# ------------------ Título ------------------
st.title("📈 Call center")

# ------------------ Dataset ------------------
df = pd.read_excel("Data/01 Call-Center-Dataset.xlsx")

# Rellenar vacíos
df["Speed of answer in seconds"] = df["Speed of answer in seconds"].fillna(0)
df["AvgTalkDuration"] = df["AvgTalkDuration"].fillna(0)
df["Satisfaction rating"] = df["Satisfaction rating"].fillna(0)

# normalizar fechas
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# ------------------ Métricas ------------------
total_llamadas = int(df["Call Id"].count())
Q_agentes = int(df["Agent"].nunique())
resueltas = int((df["Resolved"] == "Y").sum())
pct_resueltas = round((resueltas / total_llamadas) * 100, 2) if total_llamadas else 0
R_porSegundo_resueltas = round(df.loc[df["Resolved"] == "Y", "Speed of answer in seconds"].mean(), 2) if resueltas else 0
satisfaccion = round(df["Satisfaction rating"].mean(), 2) if not df["Satisfaction rating"].isna().all() else 0

# ------------------ Tarjetas personalizadas ------------------
kcol1, kcol2, kcol3, kcol4, kcol5 = st.columns(5)

card_style = """
<div style="
    background-color:#F8F9FB;
    padding:15px;
    border-radius:15px;
    text-align:center;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    border:2px solid #E5E7EB;
    height:150px;
    display:flex;
    flex-direction:column;
    justify-content:center;
">
    <h3 style="
        color:#2B2D42; 
        font-size:1.1rem; 
        margin-bottom:8px; 
        font-weight:600;
        line-height:1.2;
        word-wrap:break-word;
        white-space:normal;
    ">{}</h3>
    <h2 style="
        color:#D6457B; 
        font-size:1.8rem;
        font-weight:700; 
        margin:0;
        line-height:1.1;
    ">{}</h2>
</div>
"""

with kcol1:
    st.markdown(card_style.format("🎫 Total Llamadas", f"{total_llamadas:,}"), unsafe_allow_html=True)

with kcol3:
    st.markdown(card_style.format("✅ % Resueltas", f"{pct_resueltas}%"), unsafe_allow_html=True)

with kcol5:
    st.markdown(card_style.format("⚡ Prom. Respuesta (s)", f"{R_porSegundo_resueltas}"), unsafe_allow_html=True)

st.markdown("---")


# ------------------ Layout principal: gráfico grande + tabla/datos (sin filtros en medio) ------------------
col_left, col_right = st.columns([1.5, 1.5], gap="large")  # left más ancho, right más angosto

# ----- LEFT: Gráfico DONUT con paleta propia -----
with col_left:
    calls_por_topic = df['Topic'].value_counts().reset_index()
    calls_por_topic.columns = ['Topic', 'Count']

    fig_topic, ax_topic = plt.subplots(figsize=(7, 6))

    wedges, texts, autotexts = ax_topic.pie(
        calls_por_topic['Count'],
        labels=calls_por_topic['Topic'],
        autopct=lambda pct: f"{pct:.1f}%" if pct > 4 else "",
        startangle=90,
        pctdistance=0.75,
        labeldistance=1.05,
        colors=[PALETTE["accent"]] * len(calls_por_topic),  # MISMO COLOR DE LA PALETA
        wedgeprops={"width": 0.5, "edgecolor": PALETTE["bg"]}
    )

    # Colores de textos dentro de la paleta
    for t in texts:
        t.set_color(PALETTE["text"])
        t.set_fontsize(9)
    for at in autotexts:
        at.set_color(PALETTE["text"])
        at.set_fontweight("bold")

    ax_topic.set(aspect="equal")
    ax_topic.set_title("Llamadas por Tema", color=PALETTE["text"], pad=12)

    st.pyplot(fig_topic)

# ----- RIGHT: TABLA sin índices, respetando estilo -----
with col_right:

    df_temp = df.copy()
    df_temp['DayOfWeek'] = df_temp['Date'].dt.day_name()

    summary = (
        df_temp.groupby('DayOfWeek')
        .agg(
            Llamadas=('Call Id', 'count'),
            Atendidas=('Answered (Y/N)', lambda x: (x == 'Y').sum()),
            Resueltas=('Resolved', lambda x: (x == 'Y').sum())
        )
        .reset_index()
    )

    # Traducción y orden
    day_map = {
        'Monday':'Lunes','Tuesday':'Martes','Wednesday':'Miércoles',
        'Thursday':'Jueves','Friday':'Viernes','Saturday':'Sábado','Sunday':'Domingo'
    }
    order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    summary['DayOfWeek'] = pd.Categorical(summary['DayOfWeek'], categories=order, ordered=True)
    summary = summary.sort_values('DayOfWeek')
    summary['Día'] = summary['DayOfWeek'].map(day_map)

    # Seleccionar columnas finales y eliminar índice
    summary = summary[['Día', 'Llamadas', 'Atendidas', 'Resueltas']].reset_index(drop=True)

    # Mostrar tabla SIN índice
    st.dataframe(summary, use_container_width=True, hide_index=True)


# ------------------ GRÁFICO DE TENDENCIA ------------------
attended = df[df['Answered (Y/N)'] == 'Y'].copy()
if not attended.empty:
    attended_per_day = attended.groupby('Date').size().sort_index()
    smooth_window = 7
    attended_smooth = attended_per_day.rolling(window=smooth_window, min_periods=1, center=True).mean()

    fig_trend, ax_trend = plt.subplots(figsize=(16, 6))

    # Línea principal
    ax_trend.plot(attended_smooth.index, attended_smooth.values,
                  linewidth=2.2, color=PALETTE["accent"])

    # Relleno sutil
    ax_trend.fill_between(attended_smooth.index, attended_smooth.values,
                          alpha=0.08, color=PALETTE["accent"])

    ax_trend.set_title("Llamadas atendidas por fecha", color=PALETTE["text"], pad=14)
    ax_trend.grid(False)
    ax_trend.set_ylabel("")
    ax_trend.spines['top'].set_visible(False)
    ax_trend.spines['right'].set_visible(False)
    ax_trend.spines['left'].set_visible(False)
    ax_trend.spines['bottom'].set_color(PALETTE["muted"])

    ax_trend.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax_trend.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax_trend.get_xticklabels(), rotation=30, ha='right', color=PALETTE["muted"])

    st.pyplot(fig_trend)
