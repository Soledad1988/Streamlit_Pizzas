import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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

c1, c2 = st.columns([50, 50])

with c1:
    # Promedio satisfacción por tema
    satisfaction_by_topic = df.groupby('Topic')['Satisfaction rating'].mean().reset_index().rename(columns={'Satisfaction rating':'Avg_Satisfaction'})
    satisfaction_by_topic = satisfaction_by_topic.sort_values('Avg_Satisfaction', ascending=False)
    print("Promedio satisfacción por tema:\n", satisfaction_by_topic, "\n")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(satisfaction_by_topic['Topic'], satisfaction_by_topic['Avg_Satisfaction'])
    ax.set_xticklabels(satisfaction_by_topic['Topic'], rotation=45, ha='right')
    ax.set_ylabel('Promedio satisfacción')
    ax.set_title('Promedio de satisfacción por Tema')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig)

with c2:
    # Tabla: temas y porcentaje de resueltas / no resueltas
    topic_counts = df.groupby('Topic').agg(
        Total = ('Call Id', 'count'),
        Resueltas = ('Resolved', lambda x: (x == 'Y').sum())
    ).reset_index()
    topic_counts['No_Resueltas'] = topic_counts['Total'] - topic_counts['Resueltas']
    topic_counts['Pct_Resueltas'] = (topic_counts['Resueltas'] / topic_counts['Total'] * 100).round(2)
    topic_counts['Pct_No_Resueltas'] = (topic_counts['No_Resueltas'] / topic_counts['Total'] * 100).round(2)
    st.dataframe(topic_counts)
    
c1, c2 = st.columns([50, 50])

with c1:
   # Tabla: temas con índice de satisfacción y velocidad de respuesta (promedios)
    topic_kpis = df.groupby('Topic').agg(
        Avg_Satisfaction = ('Satisfaction rating', 'mean'),
        Avg_Speed_seconds = ('Speed of answer in seconds', 'mean'),
        Count = ('Call Id', 'count')
    ).reset_index().sort_values('Count', ascending=False)
    topic_kpis['Avg_Satisfaction'] = topic_kpis['Avg_Satisfaction'].round(2)
    topic_kpis['Avg_Speed_seconds'] = topic_kpis['Avg_Speed_seconds'].round(1)
    st.dataframe(topic_kpis)

with c2:
    # Llamadas no atendidas por tema
    not_answered_by_topic = df[df['Answered'] != 'Y'].groupby('Topic').size().reset_index(name='No_Atendidas').sort_values('No_Atendidas', ascending=False)
    print("Llamadas no atendidas por tema:\n", not_answered_by_topic, "\n")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(not_answered_by_topic['Topic'], not_answered_by_topic['No_Atendidas'])
    ax.set_xticklabels(not_answered_by_topic['Topic'], rotation=45, ha='right')
    ax.set_ylabel('Cantidad no atendidas')
    ax.set_title('Llamadas no atendidas por Tema')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig)