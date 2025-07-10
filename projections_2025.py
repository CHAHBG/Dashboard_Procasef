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
    
    # CSS personnalisé pour un design moderne avec animations ralenties
    st.markdown("""
    <style>
    body {
        background: #F7F9FB;
    }
    .main-header {
        background: linear-gradient(120deg, #6C63FF 0%, #48CAE4 100%);
        color: white;
        padding: 2.5rem 1rem 2rem 1rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(108,99,255,0.15);
        font-family: 'Montserrat', sans-serif;
    }
    .metric-card {
        background: #FFFFFF;
        padding: 2rem 1.5rem;
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(76,110,245,0.07);
        border-left: 6px solid #6C63FF;
        margin-bottom: 1.5rem;
        transition: box-shadow 0.5s ease, transform 0.5s ease;
        font-family: 'Inter', sans-serif;
    }
    .metric-card:hover {
        box-shadow: 0 8px 32px rgba(76,110,245,0.13);
        transform: translateY(-6px) scale(1.03);
    }
    .chart-container {
        background: #FFFFFF;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 24px rgba(76,110,245,0.07);
        margin-bottom: 2.5rem;
        font-family: 'Inter', sans-serif;
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
        animation: fadeIn 1.8s ease-in-out forwards;
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
            <h3 style="color: #6C63FF; margin: 0;">📌 Levés Réalisés</h3>
            <h2 style="color: #22223B; margin: 0.5rem 0;">{realises_total:,}</h2>
            <p style="color: #4a5568; margin: 0;">Total actuel</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: #6C63FF; margin: 0;">🎯 Objectif Total</h3>
            <h2 style="color: #22223B; margin: 0.5rem 0;">{objectif_total:,.0f}</h2>
            <p style="color: #4a5568; margin: 0;">Objectif 2025</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3 style="color: #6C63FF; margin: 0;">⚡ Progression</h3>
            <h2 style="color: #22223B; margin: 0.5rem 0;">{progression_pct:.1f}%</h2>
            <p style="color: #4a5568; margin: 0;">De l'objectif</p>
        </div>
        """, unsafe_allow_html=True)

    # Animation de progression lente avec st.progress
    st.markdown("### ⏳ Animation de progression lente")
    progress_bar = st.progress(0)
    for i in range(int(progression_pct)+1):
        progress_bar.progress(i)
        time.sleep(0.03)  # 30 ms entre chaque incrément pour animation fluide et lente

    # Jauge de progression avec voiture animée
    st.markdown("### 🏎️ Course vers l'Objectif")
    
    # Création de la piste avec voiture animée
    fig_race = go.Figure()
    
    # Piste de course (ligne de base)
    fig_race.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 0],
        mode='lines',
        line=dict(color='gray', width=8),
        name='Piste',
        showlegend=False
    ))
    
    # Zone de départ
    fig_race.add_shape(
        type="rect",
        x0=-2, y0=-0.5, x1=2, y1=0.5,
        fillcolor="lightgreen",
        opacity=0.3,
        line=dict(color="green", width=2),
    )
    
    # Zone d'arrivée
    fig_race.add_shape(
        type="rect",
        x0=98, y0=-0.5, x1=102, y1=0.5,
        fillcolor="gold",
        opacity=0.3,
        line=dict(color="orange", width=2),
    )
    
    # Checkpoints sur la piste
    for i in [25, 50, 75]:
        fig_race.add_shape(
            type="line",
            x0=i, y0=-0.3, x1=i, y1=0.3,
            line=dict(color="white", width=3),
        )
        fig_race.add_annotation(
            x=i, y=0.7,
            text=f"{i}%",
            showarrow=False,
            font=dict(color="darkblue", size=12)
        )
    
    # Position de la voiture basée sur la progression
    car_position = min(progression_pct, 100)
    
    # Voiture (représentée par un triangle et des formes)
    fig_race.add_trace(go.Scatter(
        x=[car_position],
        y=[0],
        mode='markers',
        marker=dict(
            size=30,
            color='red',
            symbol='triangle-right',
            line=dict(color='darkred', width=2)
        ),
        name='Voiture',
        showlegend=False
    ))
    
    # Fumée/vitesse derrière la voiture
    if car_position > 5:
        smoke_x = [car_position - 5, car_position - 3, car_position - 1]
        smoke_y = [0.1, -0.1, 0.05]
        fig_race.add_trace(go.Scatter(
            x=smoke_x,
            y=smoke_y,
            mode='markers',
            marker=dict(
                size=[8, 6, 4],
                color='lightgray',
                opacity=0.6,
                symbol='circle'
            ),
            name='Fumée',
            showlegend=False
        ))
    
    # Vitesse de la voiture (basée sur la progression)
    vitesse = "🐌 Démarrage lent"
    if progression_pct >= 75:
        vitesse = "🚀 Vitesse maximale !"
    elif progression_pct >= 50:
        vitesse = "⚡ Accélération !"
    elif progression_pct >= 25:
        vitesse = "🏃 En route !"
    
    # Annotations
    fig_race.add_annotation(
        x=0, y=-1,
        text="🏁 DÉPART",
        showarrow=False,
        font=dict(color="green", size=14, family="Arial Black")
    )
    
    fig_race.add_annotation(
        x=100, y=-1,
        text="🏆 OBJECTIF",
        showarrow=False,
        font=dict(color="orange", size=14, family="Arial Black")
    )
    
    fig_race.add_annotation(
        x=car_position, y=1,
        text=f"🏎️ {progression_pct:.1f}%",
        showarrow=True,
        arrowhead=2,
        arrowcolor="red",
        font=dict(color="red", size=16, family="Arial Black")
    )
    
    fig_race.update_layout(
        title=f"🏁 Course vers l'Objectif - {vitesse}",
        xaxis=dict(
            range=[-5, 105],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        yaxis=dict(
            range=[-1.5, 1.5],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        height=300,
        paper_bgcolor="rgba(135, 206, 235, 0.1)",  # Fond bleu ciel léger
        plot_bgcolor="rgba(144, 238, 144, 0.1)",   # Fond vert prairie léger
        font=dict(family="Arial", size=12),
        showlegend=False,
        transition={'duration': 1500, 'easing': 'cubic-in-out'}  # transition ralentie
    )
    
    st.plotly_chart(fig_race, use_container_width=True)
    
    # Jauge traditionnelle en complément
    col1, col2 = st.columns(2)
    
    with col1:
        # Compteur de vitesse style voiture
        fig_speedometer = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = progression_pct,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "🏎️ Compteur de Progression"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "red"},
                'steps': [
                    {'range': [0, 25], 'color': "lightgray"},
                    {'range': [25, 50], 'color': "yellow"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig_speedometer.update_layout(
            height=300,
            font={'color': "darkblue", 'family': "Arial"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            transition={'duration': 1500, 'easing': 'cubic-in-out'}
        )
        
        st.plotly_chart(fig_speedometer, use_container_width=True)
    
    with col2:
        # Informations de course
        st.markdown("### 📊 Informations de Course")
        
        distance_parcourue = progression_pct
        distance_restante = 100 - progression_pct
        
        st.metric("🏁 Distance parcourue", f"{distance_parcourue:.1f}%")
        st.metric("🎯 Distance restante", f"{distance_restante:.1f}%")
        
        # Messages motivants selon la position
        if progression_pct >= 100:
            st.success("🏆 **VICTOIRE !** Objectif atteint !")
        elif progression_pct >= 90:
            st.warning("🔥 **LIGNE DROITE !** Plus que quelques mètres !")
        elif progression_pct >= 75:
            st.info("⚡ **DERNIER VIRAGE !** Vous y êtes presque !")
        elif progression_pct >= 50:
            st.info("🏃 **MI-COURSE !** Bonne cadence !")
        elif progression_pct >= 25:
            st.info("🚗 **PREMIER QUART !** Continuez comme ça !")
        else:
            st.error("🏁 **DÉPART !** Accélérez pour rattraper !")

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
        ),
        transition={'duration': 1500, 'easing': 'cubic-in-out'}
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
        showlegend=True,
        transition={'duration': 1500, 'easing': 'cubic-in-out'}
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
        plot_bgcolor="rgba(0,0,0,0)",
        transition={'duration': 1500, 'easing': 'cubic-in-out'}
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


if __name__ == "__main__":
    afficher_projections_2025()
