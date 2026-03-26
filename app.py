import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION DE LA PAGE (DOIT ÊTRE LA PREMIÈRE LIGNE) ---
st.set_page_config(page_title="HydrauCalc Pro", layout="wide")

# CSS personnalisé pour réduire les marges et rendre l'interface plus compacte
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTEUR DE CALCUL ---
def calcul_physique(h, type_o, d1, d2, f, Ks, I):
    if h <= 0 or I <= 0 or Ks <= 0: return 0, 0, 0
    h_lim = min(h, d2)
    if type_o == 'Caniveau':
        S, P = d1 * h_lim, d1 + 2 * h_lim
    elif type_o == 'Fossé':
        S = (d1 + f * h_lim) * h_lim
        P = d1 + 2 * h_lim * math.sqrt(1 + f**2)
    else: # Buse
        h_b = min(h_lim, d1 * 0.999)
        theta = 2 * math.acos(1 - (2 * h_b / d1))
        S, P = (d1**2 / 8) * (theta - math.sin(theta)), (d1 * theta) / 2
    Rh = S / P if P > 0 else 0
    Q = Ks * S * (Rh**(2/3)) * math.sqrt(I)
    return Q, S, Rh

# --- BARRE LATÉRALE ---
st.sidebar.header("⚙️ Paramètres")
type_o = st.sidebar.selectbox("Ouvrage", ["Buse", "Caniveau", "Fossé"])
ks = st.sidebar.number_input("Rugosité (Ks)", value=70.0, step=1.0)
pente = st.sidebar.number_input("Pente (m/m)", value=0.01, format="%.4f", step=0.001)

# Dimensions adaptatives
if type_o == "Buse":
    d1 = st.sidebar.number_input("Diamètre (m)", value=1.0, min_value=0.1)
    d2 = d1
    fruit = 0
else:
    d1 = st.sidebar.number_input("Largeur fond (m)", value=1.0, min_value=0.1)
    d2 = st.sidebar.number_input("Hauteur totale (m)", value=0.8, min_value=0.1)
    fruit = st.sidebar.number_input("Fruit (m/m)", value=1.5) if type_o == "Fossé" else 0

h_eau = st.sidebar.slider("Hauteur d'eau (m)", 0.0, float(d2), float(d2/2), step=0.01)

# --- MISE EN PAGE PRINCIPALE ---
st.title("🌊 HydrauCalc Online")

# Calcul des résultats
q_u, s_u, rh_u = calcul_physique(h_eau, type_o, d1, d2, fruit, ks, pente)

# Affichage des métriques sur une seule ligne
m1, m2, m3 = st.columns(3)
m1.metric("Débit Capable", f"{q_u:.3f} m³/s")
m2.metric("Section Mouillée", f"{s_u:.3f} m²")
m3.metric("Vitesse Flux", f"{q_u/s_u:.2f} m/s" if s_u > 0 else "0 m/s")

st.divider()

# --- GRAPHIQUE ADAPTATIF ---
# On crée deux colonnes : le graphique à gauche, une analyse à droite
col_graph, col_info = st.columns([2, 1])

with col_graph:
    h_range = np.linspace(0.001, d2, 40)
    q_range = [calcul_physique(h, type_o, d1, d2, fruit, ks, pente)[0] for h in h_range]

    # Taille réduite (figsize) pour éviter le scroll vertical
    fig, ax = plt.subplots(figsize=(6, 3.5)) 
    ax.plot(q_range, h_range, color='#1f77b4', lw=2.5, label='Courbe de tarage')
    ax.fill_betweenx(h_range, q_range, color='#1f77b4', alpha=0.1)
    ax.axhline(h_eau, color='#d62728', linestyle='--', lw=1.5)
    ax.scatter([q_u], [h_u], color='#d62728', s=60, zorder=5)
    
    ax.set_xlabel("Débit (m³/s)", fontsize=9)
    ax.set_ylabel("Hauteur (m)", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(True, alpha=0.3)
    
    # Commande magique pour que le graphique remplisse sa colonne
    st.pyplot(fig, use_container_width=True)

with col_info:
    st.subheader("💡 Analyse")
    if h_eau > 0.8 * d2:
        st.error("⚠️ Risque de mise en charge (>80%)")
    else:
        st.success("✅ Écoulement libre stable")
    
    st.info(f"""
    **Récapitulatif :**
    - Ouvrage : {type_o}
    - Remplissage : {int(h_eau/d2*100)}%
    - Rayon Hyd. : {rh_u:.3f} m
    """)
