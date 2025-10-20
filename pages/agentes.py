import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 🩷 Configuración de la página
st.set_page_config(
    page_title="Call center",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ Título ------------------
st.title("📈 Call center")

# ------------------ Dataset ------------------
df = pd.read_excel("Data/01 Call-Center-Dataset.xlsx")

# Rellenar vacíos
df["Speed of answer in seconds"] = df["Speed of answer in seconds"].fillna(0)
df["AvgTalkDuration"] = df["AvgTalkDuration"].fillna(0)
df["Satisfaction rating"] = df["Satisfaction rating"].fillna(0)

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
x = range(len(agent_tbl_sorted))
width = 0.35
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar([i - width/2 for i in x], agent_tbl_sorted['Atendidas'], width=width, label='Atendidas')
ax.bar([i + width/2 for i in x], agent_tbl_sorted['Resueltas'], width=width, label='Resueltas')
ax.set_xticks(x)
ax.set_xticklabels(agent_tbl_sorted['Agent'], rotation=45, ha='right')
ax.set_ylabel('Cantidad')
ax.set_title('Atendidas vs Resueltas por Agente')
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
st.pyplot(fig)

c1, c2 = st.columns([60, 40])

with c1:
    # Tabla: Agentes - Total llamadas - resueltas - no resueltas
    agent_tbl = df.groupby('Agent').agg(
    Total_Llamadas = ('Call Id', 'count'),
    Atendidas = ('Answered', lambda x: (x == 'Y').sum()),
    Resueltas = ('Resolved', lambda x: (x == 'Y').sum())
    ).reset_index()
    agent_tbl['No_Resueltas'] = agent_tbl['Atendidas'] - agent_tbl['Resueltas']
    st.dataframe(agent_tbl)

with c2:
    # Asegurar que 'Date' sea tipo datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Agrupar llamadas resueltas por fecha
    resolved_ts = df[df['Resolved'] == 'Y'].groupby('Date').size().sort_index()

    # Convertir índice a DatetimeIndex (necesario para resample)
    resolved_ts.index = pd.to_datetime(resolved_ts.index)

    # Reagrupar por mes
    resolved_monthly = resolved_ts.resample('MS').sum()

    # Línea de tendencia (regresión lineal)
    x = mdates.date2num(resolved_monthly.index.to_pydatetime())
    y = resolved_monthly.values
    coef = np.polyfit(x, y, 1)
    trend = np.polyval(coef, x)

    # Crear figura y graficar
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(resolved_monthly.index, resolved_monthly.values, marker='o', label='Resueltas')
    ax.plot(resolved_monthly.index, trend, color='orange', label='Tendencia')
    ax.set_title('Tendencia llamadas resueltas')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Cantidad')
    ax.legend()
    plt.tight_layout()

    # Mostrar en Streamlit
    st.pyplot(fig)
