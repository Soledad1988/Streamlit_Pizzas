import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

#------------------------------Dashboard
st.set_page_config(
    page_title="Call center",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Call center")


# Cargamos el dataset
df = pd.read_excel("Data/01 Call-Center-Dataset.xlsx")

# Rellenamos los vacio con ceros
df["Speed of answer in seconds"] = df["Speed of answer in seconds"].fillna(0)
df["AvgTalkDuration"] = df["AvgTalkDuration"].fillna(0)
df["Satisfaction rating"] = df["Satisfaction rating"].fillna(0)

# ----------------- Cálculos -----------------
total_llamadas = df["Call Id"].count()
Q_agentes = df["Agent"].nunique()

# Porcentaje de resueltas
# Cantidad de casos resueltos
resueltas = (df["Resolved"] == "Y").sum()
# Porcentaje de resueltas
pct_resueltas = (resueltas / total_llamadas) * 100

# Promedio de segundos solo en los resueltos
R_porSegundo_resueltas = round(
    df.loc[df["Resolved"] == "Y", "Speed of answer in seconds"].mean(), 2
)

# Promedio de satisfacción solo en los resueltos
satisfaccion = round(
    df.loc[df["Resolved"] == "Y", "Satisfaction rating"].mean(), 2
)

# ----------------- Tarjetas -----------------
c1, c2, c3, c4, c5 = st.columns(5)

# Estilo de tarjeta (HTML + CSS inline)
card_style = """
    <div style="background-color:#1E1E1E;
                padding:20px;
                border-radius:15px;
                text-align:center;
                margin-bottom:25px;   /* <-- Espacio extra */
                box-shadow: 2px 2px 10px rgba(0,0,0,0.5);">
        <h3 style="color:#FFD700; font-size:22px;">{}</h3>
        <h2 style="color:white; font-size:36px; margin-top:-10px;">{}</h2>
    </div>
"""

with c1:
    st.markdown(card_style.format("🎫 Total Llamadas", total_llamadas), unsafe_allow_html=True)

with c2:
    st.markdown(card_style.format("⏱️ Cantidad de agentes", Q_agentes), unsafe_allow_html=True)

with c3:
    st.markdown(card_style.format("⚠️ Tickets Alta Prioridad", pct_resueltas), unsafe_allow_html=True)

with c4:
    st.markdown(card_style.format("⚠️ Porcentaje de resueltas", R_porSegundo_resueltas), unsafe_allow_html=True)

with c5:
    st.markdown(card_style.format("⚠️ Satisfacción", satisfaccion), unsafe_allow_html=True)