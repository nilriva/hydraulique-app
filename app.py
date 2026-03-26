import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="HydrauCalc Pro", layout="wide")

# CSS pour compacter l'affichage
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FONCTION DE CALCUL ---
def calculer_debit(h, t, d1, d2, f, Ks, I):
    if h <= 0 or I <= 0 or Ks <= 0: return 0.0, 0.0, 0.0
    h_lim = min(h, d2)
    
    if t == 'Caniveau':
        S = d1 * h_lim
        P = d1 + 2 * h_lim
    elif t == 'Fossé':
        S = (d1 + f * h_lim) * h_lim
        P = d1 + 2 * h_lim * math.sqrt(1 + f**2)
    else: # Buse
        # Sécurité pour ne pas dépasser le diamètre mathématiquement
        h_b = min(h_lim, d1 * 0.9999)
        theta = 2 * math.acos(1 - (2 * h_b / d1))
        S = (d1**2 / 8) * (theta - math.sin(theta))
        P = (d1 * theta) / 2
        
    Rh = S / P if P > 0 else 0
    Q = Ks * S * (Rh**(2/3)) * math.sqrt(I)
    return Q, S, Rh

# --- 3. BARRE LATÉRALE (SAISIES) ---
st.sidebar.header("⚙️ Paramètres")
type_o = st.sidebar.selectbox("Type d'ouvrage", ["Buse", "Caniveau", "Fossé"])
ks_val = st.sidebar.number_input("Rugosité (Ks)", value=70.0)
pente_val = st.sidebar.number_input("Pente (m/m)", value=0.01, format="%.4f")

if type_o == "Buse":
    d1_val = st.sidebar.number_input("Diamètre (m)", value=1.0)
    d2_val = d1_val # Hauteur max = Diamètre
    fruit_val = 0.0
else:
    d1_val = st.sidebar.number_input("Largeur fond (m)", value=1.0)
    d2_val = st.sidebar.number_input("Hauteur totale (m)", value=0.8)
    fruit_val = st.sidebar.number_input("Fruit (m/m)", value=1.5) if type_o == "Fossé" else 0.0

h_eau_val = st.sidebar.slider("Hauteur d'eau actuelle (m)", 0.0, float(d2_val), float(d2_val/2), step=0.01)

# --- 4. CALCULS ET RÉSULTATS ---
st.title("🌊 HydrauCalc Online")

q_u, s_u, rh_u = calculer_debit(h_eau_val, type_o, d1_val, d2_val, fruit_val, ks_val, pente_val)

# Métriques
m1, m2, m3 = st.columns(3)
m1.metric("Débit (Q)", f"{q_u:.3f} m³/s")
m2.metric("Section (S)", f"{s_u:.3f} m²")
vitesse = q_u / s_u if s_u > 0 else 0
m3.metric("Vitesse (V)", f"{vitesse:.2f} m/s")

st.divider()

# --- 5. GRAPHIQUE ET ANALYSE ---
col_graph, col_info = st.columns([2, 1])

with col_graph:
    # Génération de la courbe
    h_pts = np.linspace(0.001, d2_val, 40)
    q_pts = [calculer_debit(h, type_o, d1_val, d2_val, fruit_val, ks_val, pente_val)[0] for h in h_pts]

    fig, ax = plt.subplots(figsize=(6, 3)) # Taille ajustée pour la fenêtre
    ax.plot(q_pts, h_pts, color='#1f77b4', lw=2, label='Capacité')
    ax.fill_betweenx(h_pts, q_pts, color='#1f77b4', alpha=0.1)
    
    # Point de calcul (CORRECTION DE L'ERREUR NAMEERROR ICI)
    ax.axhline(h_eau_val, color='red', linestyle='--', lw=1)
    ax.scatter([q_u], [h_eau_val], color='red', s=50, zorder=5, label='Point actuel')
    
    ax.set_xlabel("Débit (m³/s)", fontsize=9)
    ax.set_ylabel("Hauteur (m)", fontsize=9)
    ax.grid(True, alpha=0.2)
    ax.legend(prop={'size': 8})
    
    st.pyplot(fig, use_container_width=True)

with col_info:
    st.subheader("💡 Analyse")
    ratio = (h_eau_val / d2_val) * 100
    if ratio > 85:
        st.error(f"⚠️ Risque de saturation : {ratio:.1f}%")
    elif ratio > 50:
        st.warning(f"Remplissage moyen : {ratio:.1f}%")
    else:
        st.success(f"Écoulement optimal : {ratio:.1f}%")
    
    st.info(f"Rayon Hydraulique : **{rh_u:.3f} m**")
