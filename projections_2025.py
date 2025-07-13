import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

@st.cache_data
def charger_projections():
    df = pd.read_excel("projections/Projections 2025.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower()
    return df

def animated_gauge(value, duration=1.5):
    # Animation de la jauge avec effet donut semi-circulaire
    steps = 30
    for pct in np.linspace(0, value, steps):
        fig = go.Figure(go.Pie(
            values=[pct, 100-pct],
            hole=0.7,
            marker_colors=['#FFD700', '#F0F0F0'],
            direction='clockwise',
            sort=False,
            textinfo='none',
            rotation=180,
        ))
        fig.update_traces(
            hoverinfo='skip',
            showlegend=False
        )
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            width=260, height=140,
            annotations=[dict(
                text=f"<b>{pct:.1f}%</b>",
                x=0.5, y=0.15, font_size=28, showarrow=False,
                font_color="#1A2B47"
            )],
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)
        time.sleep(duration/steps)

def afficher_projections_2025():
    st.set_page_config(
        page_title="📈 Projections 2025 - BET-PLUS",
        page_icon="📊",
        layout="wide"
    )

    st.markdown("""
    <style>
    :root {
        --main-blue: #1A2B47;
        --main-gold: #FFD700;
        --main-orange: #FF8C00;
        --main-bg: #F8F9FA;
        --card-bg: #FFFFFF;
        --card-shadow: 0 4px 24px rgba(26,43,71,0.07);
    }
    body, .stApp {
        background: var(--main-bg) !important;
        font-family: 'Poppins', sans-serif;
    }
    .metric-card-modern {
        background: var(--card-bg);
        border-radius: 18px;
        box-shadow: var(--card-shadow);
        padding: 1.5rem 1.2rem;
        margin-bottom: 1.2rem;
        transition: box-shadow 0.3s, transform 0.3s;
        border-left: 6px solid var(--main-gold);
        text-align: center;
    }
    .metric-card-modern:hover {
        box-shadow: 0 8px 32px rgba(255, 215, 0, 0.18);
        transform: translateY(-4px) scale(1.02);
    }
    .metric-title { color: var(--main-blue); font-size: 1.1rem; font-weight: 600; margin-bottom: 0.3rem;}
    .metric-value { color: var(--main-orange); font-size: 2.4rem; font-weight: 700; }
    .metric-desc { color: #6C7B8A; font-size: 0.95rem; margin-top: 0.2rem;}
    .section-title { color: var(--main-blue); font-size: 1.7rem; font-weight: 700; margin: 2rem 0 1.2rem 0;}
    .stDataFrame { background: #fff; border-radius: 12px; }
    .stButton > button { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;">
        <h1 style="color:#FFD700; font-weight:800;">📊 BET-PLUS | AUDET</h1>
        <h2 style="color:#1A2B47; font-weight:700;">Projections des Inventaires 2025</h2>
        <p style="color:#6C7B8A;">Tableau de bord interactif, moderne et animé pour le suivi des objectifs techniques</p>
    </div>
    """, unsafe_allow_html=True)

    df = charger_projections()

    # Renommage intelligent
    colonnes_cibles = {
        "mois": "mois",
        "inventaires mensuels réalisés": "realises",
        "réalisés": "realises",
        "objectif inventaires mensuels": "objectif_mensuel",
        "objectif mensuel": "objectif_mensuel",
        "objectif inventaires total": "objectif_total",
        "objectif total": "objectif_total",
    }
    colonnes_renommees = {}
    for col in df.columns:
        for cle in colonnes_cibles:
            if cle in col:
                colonnes_renommees[col] = colonnes_cibles[cle]
                break
    df = df.rename(columns=colonnes_renommees)
    colonnes_obligatoires = ["mois", "realises", "objectif_mensuel", "objectif_total"]
    for col in colonnes_obligatoires:
        if col not in df.columns:
            st.error(f"❌ La colonne requise '{col}' est introuvable dans les données.")
            st.stop()
    df = df.dropna(subset=["mois"])
    df["realises"] = pd.to_numeric(df["realises"], errors="coerce").fillna(0)
    df["objectif_mensuel"] = pd.to_numeric(df["objectif_mensuel"], errors="coerce").fillna(0)
    df["objectif_total"] = pd.to_numeric(df["objectif_total"], errors="coerce").fillna(0)

    objectif_total = df["objectif_total"].iloc[-1]
    realises_total = 31302
    progression_pct = (realises_total / objectif_total) * 100 if objectif_total else 0

    # --- Cartes de métriques modernes
    st.markdown('<div class="section-title">📊 Métriques de Performance</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card-modern">
            <div class="metric-title">🎯 Réalisés</div>
            <div class="metric-value">{:,}</div>
            <div class="metric-desc">Inventaires effectués</div>
        </div>
        """.format(realises_total), unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card-modern">
            <div class="metric-title">🏆 Objectif 2025</div>
            <div class="metric-value">{:,.0f}</div>
            <div class="metric-desc">Cible annuelle</div>
        </div>
        """.format(objectif_total), unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card-modern">
            <div class="metric-title">⚡ Taux de Réalisation</div>
            <div class="metric-value">{:.1f}%</div>
            <div class="metric-desc">Progression vers l'objectif</div>
        </div>
        """.format(progression_pct), unsafe_allow_html=True)

    # --- Progression animée
    st.markdown('<div class="section-title">🚀 Progression Dynamique</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.progress(int(progression_pct), text=f"{progression_pct:.1f}% de l’objectif atteint")
    with col2:
        animated_gauge(progression_pct)

    # --- Messages motivants animés
    if progression_pct >= 100:
        st.success("🏆 OBJECTIF ATTEINT ! Performance exceptionnelle de l'équipe technique !")
        st.balloons()
    elif progression_pct >= 90:
        st.info("🔥 EXCELLENT TRAVAIL ! Vous êtes dans la dernière ligne droite !")
    elif progression_pct >= 75:
        st.info("⚡ TRÈS BONNE PROGRESSION ! Maintenez cette cadence technique !")
    elif progression_pct >= 50:
        st.warning("🚀 BON RYTHME ! Continuez vos efforts techniques !")
    else:
        st.error("📈 POTENTIEL D'AMÉLIORATION - Mobilisation nécessaire pour rattraper les objectifs")

    # --- Graphiques modernes
    st.markdown('<div class="section-title">📊 Analyses Techniques Détaillées</div>', unsafe_allow_html=True)
    # Barres mensuelles
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df["mois"], y=df["realises"],
        name="Réalisés", marker_color='#FFD700', text=df["realises"], textposition='auto'
    ))
    fig_bar.add_trace(go.Bar(
        x=df["mois"], y=df["objectif_mensuel"],
        name="Objectif", marker_color='#1A2B47', text=df["objectif_mensuel"], textposition='auto'
    ))
    fig_bar.update_layout(
        barmode='group', plot_bgcolor='#fff', paper_bgcolor='#fff',
        xaxis_title="Période", yaxis_title="Inventaires",
        legend=dict(bgcolor='rgba(255,255,255,0.8)', borderwidth=1),
        height=400, margin=dict(t=40, b=40, l=20, r=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Tableau de données épuré
    st.markdown('<div class="section-title">📋 Données Techniques Détaillées</div>', unsafe_allow_html=True)
    df['perf_pct'] = (df['realises'] / df['objectif_mensuel'] * 100).fillna(0)
    df_display = df.copy()
    df_display['Performance (%)'] = df_display['perf_pct'].round(1)
    df_display['Écart'] = df_display['realises'] - df_display['objectif_mensuel']
    df_display = df_display.rename(columns={
        'mois': 'Période',
        'realises': 'Inventaires Réalisés',
        'objectif_mensuel': 'Objectif Technique',
        'objectif_total': 'Objectif Cumulé'
    })
    df_display = df_display[['Période', 'Inventaires Réalisés', 'Objectif Technique', 'Objectif Cumulé', 'Performance (%)', 'Écart']]
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Performance (%)': st.column_config.ProgressColumn(
                'Performance (%)',
                help='Pourcentage de réalisation de l\'objectif technique mensuel',
                format='%.1f%%',
                min_value=0,
                max_value=100,
            ),
        }
    )

    # --- Actions rapides
    st.markdown('<div class="section-title">⚡ Actions Rapides</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Actualiser les données"):
            st.rerun()
    with col2:
        if st.button("📊 Exporter le rapport"):
            st.info("Fonctionnalité d'export en cours de développement")
    with col3:
        if st.button("🎉 Message de motivation"):
            st.balloons()
            st.success("🌟 Bravo à toute l'équipe BET-PLUS/AUDET ! Votre travail technique fait la différence ! 💪")

if __name__ == "__main__":
    afficher_projections_2025()
