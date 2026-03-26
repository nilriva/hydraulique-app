import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="HydrauCalc Pro", layout="wide")

st.title("🌊 HydrauCalc Pro v10.0")
st.markdown("Outil de dimensionnement hydraulique pour buses, caniveaux et fossés.")

# --- BARRE LATÉRALE (PARAMÈTRES) ---
st.sidebar.header("⚙️ Paramètres de l'ouvrage")

type_o = st.sidebar.selectbox("Type d'ouvrage", ["Buse", "Caniveau", "Fossé"])
ks = st.sidebar.number_input("Rugosité (Ks)", value=70.0)
pente = st.sidebar.number_input("Pente (m/m)", value=0.01, format="%.4f")

# Dimensions dynamiques
d1 = st.sidebar.number_input("Diamètre" if type_o == "Buse" else "Largeur fond (m)", value=1.0)
d2 = d1 if type_o == "Buse" else st.sidebar.number_input("Hauteur totale (m)", value=0.8)
fruit = st.sidebar.number_input("Fruit des berges (m/m)", value=1.5) if type_o == "Fossé" else 0
h_eau = st.sidebar.slider("Hauteur d'eau actuelle (m)", 0.0, float(d2), 0.4)

# --- MOTEUR DE CALCUL ---
def calculer(h, t, d1, d2, f, Ks, I):
    if h <= 0 or I <= 0: return 0, 0, 0
    h_lim = min(h, d2)
    if t == 'Caniveau':
        S, P = d1 * h_lim, d1 + 2 * h_lim
    elif t == 'Fossé':
        S = (d1 + f * h_lim) * h_lim
        P = d1 + 2 * h_lim * math.sqrt(1 + f**2)
    else: # Buse
        theta = 2 * math.acos(1 - (2 * min(h_lim, d1*0.999) / d1))
        S, P = (d1**2 / 8) * (theta - math.sin(theta)), (d1 * theta) / 2
    Rh = S / P if P > 0 else 0
    Q = Ks * S * (Rh**(2/3)) * math.sqrt(I)
    return Q, S, Rh

# --- AFFICHAGE DES RÉSULTATS ---
q_u, s_u, rh_u = calculer(h_eau, type_o, d1, d2, fruit, ks, pente)

col1, col2, col3 = st.columns(3)
col1.metric("Débit Q", f"{q_u:.3f} m³/s")
col2.metric("Section S", f"{s_u:.3f} m²")
col3.metric("Vitesse V", f"{q_u/s_u:.2f} m/s" if s_u > 0 else "0 m/s")

# --- GRAPHIQUE ---
h_range = np.linspace(0.01, d2, 50)
q_range = [calculer(h, type_o, d1, d2, fruit, ks, pente)[0] for h in h_range]

fig, ax = plt.subplots()
ax.plot(q_range, h_range, color="#1E88E5", lw=3)
ax.axhline(h_eau, color="red", linestyle="--")
ax.set_xlabel("Débit (m³/s)")
ax.set_ylabel("Hauteur (m)")
st.pyplot(fig)