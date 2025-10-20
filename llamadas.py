import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import datetime

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


# ------------------ Métricas ------------------
total_llamadas = df["Call Id"].count()
Q_agentes = df["Agent"].nunique()
resueltas = (df["Resolved"] == "Y").sum()
pct_resueltas = round((resueltas / total_llamadas) * 100, 2)
R_porSegundo_resueltas = round(df.loc[df["Resolved"] == "Y", "Speed of answer in seconds"].mean(), 2)
satisfaccion = round(df.loc[df["Resolved"] == "Y", "Satisfaction rating"].mean(), 2)

# ------------------ Tarjetas ------------------
c1, c2, c3, c4, c5 = st.columns(5)
card_style = """
<div style="background-color:#ffe6f2;
            padding:20px;
            border-radius:15px;
            text-align:center;
            margin-bottom:25px;
            box-shadow: 1px 1px 6px rgba(255,105,180,0.4);">
    <h4 style="color:#d63384;">{}</h4>
    <h2 style="color:#8b0057;">{}</h2>
</div>
"""
with c1:
    st.markdown(card_style.format("🎫 Total Llamadas", total_llamadas), unsafe_allow_html=True)
with c2:
    st.markdown(card_style.format("👩‍💻 Agentes", Q_agentes), unsafe_allow_html=True)
with c3:
    st.markdown(card_style.format("✅ % Resueltas", f"{pct_resueltas}%"), unsafe_allow_html=True)
with c4:
    st.markdown(card_style.format("⚡ Promedio Respuesta", R_porSegundo_resueltas), unsafe_allow_html=True)
with c5:
    st.markdown(card_style.format("⭐ Satisfacción", satisfaccion), unsafe_allow_html=True)

# ------------------ Gráficos ------------------
c1, c2 = st.columns([60, 40])

with c1:
    calls_por_topic = df['Topic'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(calls_por_topic.values,
            labels=calls_por_topic.index,
            autopct='%1.1f%%',
            startangle=90)
    ax1.set_title("Llamadas por Tema", color="#8b0057")
    st.pyplot(fig1)

with c2:
    df['Date'] = pd.to_datetime(df['Date'])
    df['DayOfWeek'] = df['Date'].dt.day_name()
    summary = df.groupby('DayOfWeek').agg({
        'Resolved': lambda x: (x == 'Y').sum(),
        'Answered (Y/N)': lambda x: (x == 'Y').sum()
    }).reset_index()
    summary.columns = ['Día de la semana', 'Resueltas', 'Atendidas']
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    summary['Día de la semana'] = pd.Categorical(summary['Día de la semana'], categories=order, ordered=True)
    summary = summary.sort_values('Día de la semana')
    st.dataframe(summary)

# ------------------ Gráfico de líneas ------------------
attended = df[df['Answered (Y/N)'] == 'Y']
attended_per_day = attended.groupby('Date').size()

fig2, ax2 = plt.subplots()
ax2.plot(attended_per_day.index, attended_per_day.values, color="#d63384")
ax2.set_title("Llamadas Atendidas por Fecha", color="#8b0057")
ax2.set_xlabel("Fecha")
ax2.set_ylabel("Cantidad")
ax2.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig2)
