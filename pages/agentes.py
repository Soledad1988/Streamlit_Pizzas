import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
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
st.title("👩‍💻 Agentes")

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
    st.markdown(card_style.format("👩‍💻 Agentes", f"{Q_agentes}"), unsafe_allow_html=True)
with kcol3:
    st.markdown(card_style.format("✅ % Resueltas", f"{pct_resueltas}%"), unsafe_allow_html=True)
with kcol5:
    st.markdown(card_style.format("⭐ Satisfacción", f"{satisfaccion}"), unsafe_allow_html=True)

st.markdown("---")

# Normalizar columnas clave
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Answered'] = df['Answered (Y/N)'].fillna('N').astype(str)
df['Resolved'] = df['Resolved'].fillna('N').astype(str)
df['Speed of answer in seconds'] = pd.to_numeric(df['Speed of answer in seconds'], errors='coerce').fillna(0)
df['Satisfaction rating'] = pd.to_numeric(df['Satisfaction rating'], errors='coerce').fillna(0)

# Tabla: Agentes - Total llamadas - resueltas - no resueltas
agent_tbl = df.groupby('Agent').agg(
    Total_Llamadas = ('Call Id', 'count'),
    Atendidas = ('Answered', lambda x: (x == 'Y').sum()),
    Resueltas = ('Resolved', lambda x: (x == 'Y').sum())
).reset_index()
agent_tbl['No_Resueltas'] = agent_tbl['Atendidas'] - agent_tbl['Resueltas']

# Gráfico 1: Llamadas atendidas vs resueltas por agente (barras agrupadas)
agent_tbl_sorted = agent_tbl.sort_values('Total_Llamadas', ascending=False)
x = np.arange(len(agent_tbl_sorted))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 5))

# Barras
bars1 = ax.bar(x - width/2, agent_tbl_sorted['Atendidas'], width=width, label='Atendidas', color=PALETTE["accent"])
bars2 = ax.bar(x + width/2, agent_tbl_sorted['Resueltas'], width=width, label='Resueltas', color=PALETTE["text"])

# Etiquetas de valores sobre las barras
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), int(bar.get_height()), 
            ha='center', va='bottom', fontsize=9, color=PALETTE["text"])
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), int(bar.get_height()), 
            ha='center', va='bottom', fontsize=9, color=PALETTE["text"])

# Eliminar fondo, bordes y líneas de grilla
ax.set_facecolor(PALETTE["bg"])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.grid(False)

# Eje X
ax.set_xticks(x)
ax.set_xticklabels(agent_tbl_sorted['Agent'], rotation=45, ha='right', color=PALETTE["text"])

# Quitar etiqueta del eje Y
ax.set_ylabel("")

# Título
ax.set_title('Atendidas vs Resueltas por Agente', color=PALETTE["text"], pad=10)

# Leyenda centrada
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)

plt.tight_layout()
st.pyplot(fig)

st.markdown("---")

c1, c2 = st.columns([40, 60])

# ================== 📊 TABLA SIN ÍNDICE ==================
with c1:
    agent_tbl = df.groupby('Agent').agg(
        Total_Llamadas=('Call Id', 'count'),
        Atendidas=('Answered', lambda x: (x == 'Y').sum()),
        Resueltas=('Resolved', lambda x: (x == 'Y').sum())
    ).reset_index()
    agent_tbl['No_Resueltas'] = agent_tbl['Atendidas'] - agent_tbl['Resueltas']

    # Mostrar tabla sin índice
    st.dataframe(
        agent_tbl.style.set_properties(
            **{
                'background-color': PALETTE["card_bg"],
                'color': PALETTE["text"],
                'border-color': PALETTE["muted"]
            }
        ),
        use_container_width=True,
        hide_index=True
    )

# ================== 📈 GRÁFICO DE TENDENCIA (Más alto) ==================
with c2:
    df['Date'] = pd.to_datetime(df['Date'])
    resolved_ts = df[df['Resolved'] == 'Y'].groupby('Date').size().sort_index()
    resolved_ts.index = pd.to_datetime(resolved_ts.index)

    resolved_monthly = resolved_ts.resample('MS').sum()

    # Regresión lineal (tendencia)
    x = mdates.date2num(resolved_monthly.index.to_pydatetime())
    y = resolved_monthly.values
    coef = np.polyfit(x, y, 1)
    trend = np.polyval(coef, x)

    # --- Gráfico más alto (figsize aumentado) ---
    fig, ax = plt.subplots(figsize=(10, 6))  # <-- Aquí se hace más alto

    ax.plot(resolved_monthly.index, resolved_monthly.values, marker='o', linewidth=2,
            label='Resueltas', color=PALETTE["accent"])
    ax.plot(resolved_monthly.index, trend, linestyle='--', linewidth=1.8,
            label='Tendencia', color=PALETTE["text"])

    # Etiquetas de datos sobre los puntos
    for x_val, y_val in zip(resolved_monthly.index, resolved_monthly.values):
        ax.text(x_val, y_val, f"{int(y_val)}", ha='center', va='bottom', fontsize=8, color=PALETTE["text"])

    # Estilo visual minimalista
    ax.set_facecolor(PALETTE["bg"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)

    ax.set_title('📈 Tendencia de llamadas resueltas', fontsize=12, color=PALETTE["text"])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='both', colors=PALETTE["muted"])

    # Leyenda centrada debajo
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)

    plt.tight_layout()
    st.pyplot(fig)
