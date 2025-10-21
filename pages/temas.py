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
st.title("⭐ Temas")

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
    <h3 style="color:#2B2D42; font-size:1.3rem; margin-bottom:8px; font-weight:600;">{}</h3>
    <h2 style="color:#D6457B; font-size:2rem; font-weight:700; margin:0;">{}</h2>
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


# ========================== DISTRIBUCIÓN MEJORADA ==========================

# Primer bloque: gráfico + tabla (55 / 45)
c1, c2 = st.columns([55, 45])

# 📊 Promedio satisfacción por tema
with c1:
    satisfaction_by_topic = df.groupby('Topic')['Satisfaction rating'].mean().reset_index()
    satisfaction_by_topic = satisfaction_by_topic.sort_values('Satisfaction rating', ascending=False)

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(satisfaction_by_topic['Topic'], satisfaction_by_topic['Satisfaction rating'], 
                  color=PALETTE["accent"])

    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                f"{bar.get_height():.2f}", ha='center', va='bottom', 
                fontsize=9, color=PALETTE["text"])

    for spine in ax.spines.values(): spine.set_visible(False)
    ax.set_xticklabels(satisfaction_by_topic['Topic'], rotation=45, ha='right', color=PALETTE["text"])
    ax.set_title('Promedio de satisfacción por Tema', color=PALETTE["text"])
    st.pyplot(fig)

# 📋 Tabla: temas resueltos y no resueltos
with c2:
    topic_counts = df.groupby('Topic').agg(
        Total=('Call Id', 'count'),
        Resueltas=('Resolved', lambda x: (x == 'Y').sum())
    ).reset_index()

    topic_counts['No_Resueltas'] = topic_counts['Total'] - topic_counts['Resueltas']
    topic_counts['% Resueltas'] = (topic_counts['Resueltas'] / topic_counts['Total'] * 100).round(1)

    st.dataframe(
        topic_counts.style.set_properties(
            **{'background-color': PALETTE["card_bg"], 'color': PALETTE["text"]}
        ),
        use_container_width=True,
        hide_index=True
    )

# Segundo bloque: tabla KPI + gráfico (50 / 50)
c3, c4 = st.columns([50, 50])

# 📋 KPI por tema
with c3:
    topic_kpis = df.groupby('Topic').agg(
        Prom_Satisfacción=('Satisfaction rating', 'mean'),
        Prom_Speed=('Speed of answer in seconds', 'mean'),
        Llamadas=('Call Id', 'count')
    ).reset_index().sort_values('Llamadas', ascending=False)

    topic_kpis['Prom_Satisfacción'] = topic_kpis['Prom_Satisfacción'].round(2)
    topic_kpis['Prom_Speed'] = topic_kpis['Prom_Speed'].round(1)

    st.dataframe(
        topic_kpis.style.set_properties(
            **{'background-color': PALETTE["card_bg"], 'color': PALETTE["text"]}
        ),
        use_container_width=True,
        hide_index=True
    )

# 📊 Llamadas no atendidas por tema
with c4:
    not_answered = df[df['Answered'] != 'Y'].groupby('Topic').size().reset_index(name='No_Atendidas')
    not_answered = not_answered.sort_values('No_Atendidas', ascending=False)

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(not_answered['Topic'], not_answered['No_Atendidas'], color=PALETTE["text"])

    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                f"{int(bar.get_height())}", ha='center', va='bottom', 
                fontsize=9, color=PALETTE["text"])

    for spine in ax.spines.values(): spine.set_visible(False)
    ax.set_xticklabels(not_answered['Topic'], rotation=45, ha='right', color=PALETTE["text"])
    ax.set_title('Llamadas no atendidas por Tema', color=PALETTE["text"])
    ax.grid(False)
    st.pyplot(fig)
