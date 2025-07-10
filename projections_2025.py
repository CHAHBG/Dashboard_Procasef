import streamlit as st
import pandas as pd
import altair as alt
import time
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np


@st.cache_data
def charger_projections():
    df = pd.read_excel("projections/Projections 2025.xlsx", engine="openpyxl")
    # Nettoyage des noms de colonnes
    df.columns = df.columns.str.strip().str.lower()
    return df


def afficher_projections_2025():
    # Configuration de la page avec un style moderne
    st.set_page_config(
        page_title="📈 Projections 2025",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # CSS personnalisé pour un design moderne
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .progress-ring {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .fade-in {
        animation: fadeIn 1s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    # En-tête principal avec animation
    st.markdown("""
    <div class="main-header fade-in">
        <h1>📊 Projections des Inventaires - 2025</h1>
        <p>Tableau de bord interactif pour le suivi de vos objectifs</p>
    </div>
    """, unsafe_allow_html=True)

    df = charger_projections()

    # Tentative intelligente de renommage automatique
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

    dernier_mois = df["mois"].iloc[-1]
    objectif_total = df["objectif_total"].iloc[-1]
    realises_total = 28968
    progression_pct = (realises_total / objectif_total) * 100 if objectif_total else 0

    # Section métriques avec cartes modernes
    st.markdown("### 📊 Métriques Clés")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: #667eea; margin: 0;">📌 Levés Réalisés</h3>
            <h2 style="color: #2d3748; margin: 0.5rem 0;">{realises_total:,}</h2>
            <p style="color: #4a5568; margin: 0;">Total actuel</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: #667eea; margin: 0;">🎯 Objectif Total</h3>
            <h2 style="color: #2d3748; margin: 0.5rem 0;">{objectif_total:,.0f}</h2>
            <p style="color: #4a5568; margin: 0;">Objectif 2025</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: #667eea; margin: 0;">⚡ Progression</h3>
            <h2 style="color: #2d3748; margin: 0.5rem 0;">{progression_pct:.1f}%</h2>
            <p style="color: #4a5568; margin: 0;">De l'objectif</p>
        </div>
        """, unsafe_allow_html=True)

    # Jauge de progression animée avec Plotly
    st.markdown("### 🎯 Jauge de Progression")
    
    # Création de la jauge avec Plotly
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = progression_pct,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Progression de l'Objectif"},
        delta = {'reference': 100, 'increasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 25], 'color': "lightgray"},
                {'range': [25, 50], 'color': "gray"},
                {'range': [50, 75], 'color': "lightblue"},
                {'range': [75, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=400,
        font={'color': "darkblue", 'family': "Arial"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Graphique en barres interactif avec Plotly
    st.markdown("### 📊 Suivi Mensuel : Objectifs vs Réalisés")
    
    fig_bar = go.Figure()
    
    fig_bar.add_trace(go.Bar(
        x=df["mois"],
        y=df["realises"],
        name="Réalisés",
        marker_color='rgba(46, 204, 113, 0.8)',
        text=df["realises"],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Réalisés: %{y}<extra></extra>'
    ))
    
    fig_bar.add_trace(go.Bar(
        x=df["mois"],
        y=df["objectif_mensuel"],
        name="Objectif Mensuel",
        marker_color='rgba(52, 152, 219, 0.8)',
        text=df["objectif_mensuel"],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Objectif: %{y}<extra></extra>'
    ))
    
    fig_bar.update_layout(
        title="Comparaison Mensuelle",
        xaxis_title="Mois",
        yaxis_title="Nombre d'Inventaires",
        barmode='group',
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig_bar.update_traces(
        marker_line_color='white',
        marker_line_width=1.5,
        opacity=0.8
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

    # Graphique d'évolution avec zone remplie
    st.markdown("### 📈 Évolution de l'Objectif Cumulé")
    
    fig_area = go.Figure()
    
    # Zone d'objectif cumulé
    fig_area.add_trace(go.Scatter(
        x=df["mois"],
        y=df["objectif_total"],
        fill='tozeroy',
        mode='lines+markers',
        name='Objectif Cumulé',
        line=dict(color='rgba(52, 152, 219, 0.8)', width=3),
        fillcolor='rgba(52, 152, 219, 0.2)',
        hovertemplate='<b>%{x}</b><br>Objectif: %{y:,.0f}<extra></extra>'
    ))
    
    # Ligne horizontale pour les levés actuels
    fig_area.add_hline(
        y=realises_total,
        line_dash="dash",
        line_color="green",
        line_width=3,
        annotation_text=f"Levés actuels: {realises_total:,}",
        annotation_position="top right"
    )
    
    fig_area.update_layout(
        title="Progression vers l'Objectif Total",
        xaxis_title="Mois",
        yaxis_title="Nombre d'Inventaires",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", size=12),
        showlegend=True
    )
    
    st.plotly_chart(fig_area, use_container_width=True)

    # Graphique radar pour une vue d'ensemble
    st.markdown("### 🎯 Performance par Mois (Vue Radar)")
    
    # Calcul du pourcentage de réalisation par mois
    df['perf_pct'] = (df['realises'] / df['objectif_mensuel'] * 100).fillna(0)
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=df['perf_pct'],
        theta=df['mois'],
        fill='toself',
        name='Performance (%)',
        line_color='rgba(46, 204, 113, 0.8)',
        fillcolor='rgba(46, 204, 113, 0.2)'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(df['perf_pct'].max() * 1.1, 100)]
            )),
        showlegend=True,
        title="Performance Mensuelle (%)",
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

    # Tableau de données avec style moderne
    st.markdown("### 📋 Données Détaillées")
    
    # Ajouter une colonne de performance
    df_display = df.copy()
    df_display['Performance (%)'] = df_display['perf_pct'].round(1)
    df_display['Écart'] = df_display['realises'] - df_display['objectif_mensuel']
    
    # Formatage des colonnes
    df_display['realises'] = df_display['realises'].apply(lambda x: f"{x:,.0f}")
    df_display['objectif_mensuel'] = df_display['objectif_mensuel'].apply(lambda x: f"{x:,.0f}")
    df_display['objectif_total'] = df_display['objectif_total'].apply(lambda x: f"{x:,.0f}")
    df_display['Écart'] = df_display['Écart'].apply(lambda x: f"{x:+,.0f}")
    
    # Renommer les colonnes pour l'affichage
    df_display = df_display.rename(columns={
        'mois': 'Mois',
        'realises': 'Réalisés',
        'objectif_mensuel': 'Objectif Mensuel',
        'objectif_total': 'Objectif Cumulé'
    })
    
    # Sélectionner les colonnes à afficher
    df_display = df_display[['Mois', 'Réalisés', 'Objectif Mensuel', 'Objectif Cumulé', 'Performance (%)', 'Écart']]
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Performance (%)': st.column_config.ProgressColumn(
                'Performance (%)',
                help='Pourcentage de réalisation de l\'objectif mensuel',
                format='%.1f%%',
                min_value=0,
                max_value=100,
            ),
        }
    )

    # Section d'insights avec animation
    st.markdown("### 💡 Insights Clés")
    
    # Calculs pour les insights
    mois_meilleur = df.loc[df['perf_pct'].idxmax(), 'mois']
    meilleure_perf = df['perf_pct'].max()
    moyenne_perf = df['perf_pct'].mean()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"🏆 **Meilleur mois**: {mois_meilleur} ({meilleure_perf:.1f}%)")
    
    with col2:
        st.info(f"📊 **Performance moyenne**: {moyenne_perf:.1f}%")
    
    with col3:
        mois_restants = 12 - len(df)
        if mois_restants > 0:
            st.info(f"📅 **Mois restants**: {mois_restants} mois")
        else:
            st.success("✅ **Année complète analysée**")

    # Animation de fin avec un message motivant
    if progression_pct >= 100:
        st.balloons()
        st.success("🎉 Félicitations ! Objectif atteint !")
    elif progression_pct >= 90:
        st.warning("⚡ Presque au but ! Encore un petit effort !")
    elif progression_pct >= 75:
        st.info("💪 Bonne progression ! Continuez sur cette lancée !")
    else:
        st.error("🚀 Il est temps d'accélérer pour atteindre l'objectif !")
