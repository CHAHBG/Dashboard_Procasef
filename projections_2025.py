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

    # Jauge de progression avec voiture animée - SUPER ATTRACTIF
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
            🏎️ COURSE VERS L'OBJECTIF 🏆
        </h2>
        <p style="font-size: 1.2rem; color: #666; font-weight: 500;">
            Votre progression en temps réel !
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Création de la piste avec voiture animée ULTRA ATTRACTIVE
    fig_race = go.Figure()
    
    # Piste de course dégradée (multiple lignes pour effet 3D)
    for i, (width, color, opacity) in enumerate([(20, '#2C3E50', 0.3), (16, '#34495E', 0.5), (12, '#95A5A6', 0.7), (8, '#BDC3C7', 0.9)]):
        fig_race.add_trace(go.Scatter(
            x=[0, 100],
            y=[0, 0],
            mode='lines',
            line=dict(color=color, width=width),
            opacity=opacity,
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Ligne centrale de la piste (pointillés)
    fig_race.add_trace(go.Scatter(
        x=list(range(5, 96, 10)),
        y=[0] * len(list(range(5, 96, 10))),
        mode='markers',
        marker=dict(color='white', size=3, symbol='line-ns'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Zone de départ avec effet brillant
    fig_race.add_shape(
        type="rect",
        x0=-3, y0=-1.2, x1=3, y1=1.2,
        fillcolor="rgba(46, 204, 113, 0.8)",
        line=dict(color="#27AE60", width=3),
    )
    
    # Zone d'arrivée avec effet brillant
    fig_race.add_shape(
        type="rect",
        x0=97, y0=-1.2, x1=103, y1=1.2,
        fillcolor="rgba(241, 196, 15, 0.8)",
        line=dict(color="#F39C12", width=3),
    )
    
    # Checkpoints colorés et animés
    checkpoint_colors = ['#E74C3C', '#9B59B6', '#3498DB', '#1ABC9C']
    for i, checkpoint in enumerate([25, 50, 75, 90]):
        fig_race.add_shape(
            type="rect",
            x0=checkpoint-1, y0=-0.8, x1=checkpoint+1, y1=0.8,
            fillcolor=f"rgba({int(checkpoint_colors[i % 4][1:3], 16)}, {int(checkpoint_colors[i % 4][3:5], 16)}, {int(checkpoint_colors[i % 4][5:7], 16)}, 0.4)",
            line=dict(color=checkpoint_colors[i % 4], width=2),
        )
        fig_race.add_annotation(
            x=checkpoint, y=1.5,
            text=f"🏁 {checkpoint}%",
            showarrow=False,
            font=dict(color=checkpoint_colors[i % 4], size=14, family="Arial Black"),
            bgcolor="white",
            bordercolor=checkpoint_colors[i % 4],
            borderwidth=2
        )
    
    # Position de la voiture basée sur la progression
    car_position = min(progression_pct, 100)
    
    # Voiture SUPER STYLÉE avec multiple éléments
    # Corps de la voiture
    fig_race.add_trace(go.Scatter(
        x=[car_position],
        y=[0],
        mode='markers',
        marker=dict(
            size=45,
            color='#E74C3C',
            symbol='diamond',
            line=dict(color='#C0392B', width=3)
        ),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Phares de la voiture
    fig_race.add_trace(go.Scatter(
        x=[car_position + 1],
        y=[0],
        mode='markers',
        marker=dict(
            size=15,
            color='#F1C40F',
            symbol='circle',
            line=dict(color='#F39C12', width=2)
        ),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Fumée/vitesse derrière la voiture (plus stylée)
    if car_position > 5:
        smoke_positions = [(car_position - 8, 0.2), (car_position - 6, -0.2), (car_position - 4, 0.1), (car_position - 2, -0.1)]
        for i, (x, y) in enumerate(smoke_positions):
            fig_race.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers',
                marker=dict(
                    size=20 - i*3,
                    color='rgba(149, 165, 166, 0.6)',
                    symbol='circle',
                    line=dict(color='rgba(127, 140, 141, 0.8)', width=1)
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Étincelles/boost si progression > 75%
    if progression_pct > 75:
        for i in range(3):
            fig_race.add_trace(go.Scatter(
                x=[car_position - 2 - i],
                y=[0.3 * (-1)**i],
                mode='markers',
                marker=dict(
                    size=8,
                    color='#F39C12',
                    symbol='star',
                    line=dict(color='#E67E22', width=1)
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Vitesse de la voiture (basée sur la progression)
    vitesse_info = {
        (0, 25): ("🐌 DÉMARRAGE", "#95A5A6"),
        (25, 50): ("🏃 EN ROUTE", "#3498DB"),
        (50, 75): ("⚡ ACCÉLÉRATION", "#9B59B6"),
        (75, 90): ("🚀 TURBO MODE", "#E67E22"),
        (90, 100): ("🔥 VITESSE MAX", "#E74C3C"),
        (100, 101): ("🏆 CHAMPION", "#F1C40F")
    }
    
    vitesse_text, vitesse_color = next((text, color) for (min_val, max_val), (text, color) in vitesse_info.items() if min_val <= progression_pct < max_val)
    
    # Annotations avec style amélioré
    fig_race.add_annotation(
        x=0, y=-2,
        text="🏁 DÉPART",
        showarrow=False,
        font=dict(color="#27AE60", size=18, family="Arial Black"),
        bgcolor="rgba(46, 204, 113, 0.2)",
        bordercolor="#27AE60",
        borderwidth=2
    )
    
    fig_race.add_annotation(
        x=100, y=-2,
        text="🏆 VICTOIRE",
        showarrow=False,
        font=dict(color="#F39C12", size=18, family="Arial Black"),
        bgcolor="rgba(241, 196, 15, 0.2)",
        bordercolor="#F39C12",
        borderwidth=2
    )
    
    # Annotation voiture avec bulle stylée
    fig_race.add_annotation(
        x=car_position, y=2,
        text=f"🏎️ {progression_pct:.1f}%",
        showarrow=True,
        arrowhead=2,
        arrowcolor=vitesse_color,
        arrowwidth=3,
        font=dict(color=vitesse_color, size=20, family="Arial Black"),
        bgcolor="white",
        bordercolor=vitesse_color,
        borderwidth=3
    )
    
    # Décoration du fond avec nuages
    for i, x in enumerate([15, 35, 60, 85]):
        fig_race.add_annotation(
            x=x, y=2.5,
            text="☁️",
            showarrow=False,
            font=dict(color="rgba(255, 255, 255, 0.7)", size=20)
        )
    
    # Soleil
    fig_race.add_annotation(
        x=90, y=3,
        text="☀️",
        showarrow=False,
        font=dict(color="#F1C40F", size=25)
    )
    
    fig_race.update_layout(
        title=dict(
            text=f"<b style='color: {vitesse_color}; font-size: 24px;'>{vitesse_text}</b>",
            x=0.5,
            font=dict(size=24, family="Arial Black")
        ),
        xaxis=dict(
            range=[-8, 108],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        yaxis=dict(
            range=[-2.5, 3.5],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        height=400,
        paper_bgcolor="linear-gradient(135deg, #74b9ff, #0984e3)",
        plot_bgcolor="rgba(116, 185, 255, 0.1)",
        font=dict(family="Arial", size=12),
        showlegend=False
    )
    
    st.plotly_chart(fig_race, use_container_width=True)
    
    # Compteurs stylés avec design gaming
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 20px; color: white; text-align: center; 
                    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);">
            <h3 style="margin: 0; font-size: 1.8rem;">🏎️ COMPTEUR DIGITAL</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Compteur de vitesse style gaming
        fig_speedometer = go.Figure()
        
        # Cercle extérieur
        fig_speedometer.add_trace(go.Scatter(
            x=[0], y=[0],
            mode='markers',
            marker=dict(
                size=200,
                color='rgba(0,0,0,0)',
                line=dict(color='#2C3E50', width=8)
            ),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Secteurs colorés
        angles = np.linspace(0, 2*np.pi, 100)
        for i, (start, end, color) in enumerate([(0, 0.25, '#E74C3C'), (0.25, 0.5, '#F39C12'), (0.5, 0.75, '#F1C40F'), (0.75, 1, '#2ECC71')]):
            sector_angles = angles[int(start*100):int(end*100)]
            if len(sector_angles) > 0:
                x_coords = [0] + [0.8 * np.cos(a - np.pi/2) for a in sector_angles] + [0]
                y_coords = [0] + [0.8 * np.sin(a - np.pi/2) for a in sector_angles] + [0]
                fig_speedometer.add_trace(go.Scatter(
                    x=x_coords, y=y_coords,
                    fill='toself',
                    fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.3)',
                    line=dict(color=color, width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # Aiguille
        needle_angle = (progression_pct / 100) * 2 * np.pi - np.pi/2
        needle_x = [0, 0.7 * np.cos(needle_angle)]
        needle_y = [0, 0.7 * np.sin(needle_angle)]
        fig_speedometer.add_trace(go.Scatter(
            x=needle_x, y=needle_y,
            mode='lines',
            line=dict(color='#C0392B', width=6),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Centre du compteur
        fig_speedometer.add_trace(go.Scatter(
            x=[0], y=[0],
            mode='markers',
            marker=dict(size=30, color='#2C3E50'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Chiffres sur le compteur
        for i in range(5):
            angle = i * np.pi/2 - np.pi/2
            x_pos = 0.9 * np.cos(angle)
            y_pos = 0.9 * np.sin(angle)
            fig_speedometer.add_annotation(
                x=x_pos, y=y_pos,
                text=str(i * 25),
                showarrow=False,
                font=dict(color='white', size=16, family="Arial Black")
            )
        
        # Valeur centrale
        fig_speedometer.add_annotation(
            x=0, y=-0.3,
            text=f"{progression_pct:.1f}%",
            showarrow=False,
            font=dict(color='white', size=24, family="Arial Black")
        )
        
        fig_speedometer.update_layout(
            xaxis=dict(range=[-1.2, 1.2], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[-1.2, 1.2], showgrid=False, zeroline=False, showticklabels=False),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        
        st.plotly_chart(fig_speedometer, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff7b7b 0%, #667eea 100%); 
                    padding: 1.5rem; border-radius: 20px; color: white; text-align: center; 
                    box-shadow: 0 15px 35px rgba(255, 123, 123, 0.3);">
            <h3 style="margin: 0; font-size: 1.8rem;">📊 STATS DE COURSE</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Informations de course avec style gaming
        distance_parcourue = progression_pct
        distance_restante = 100 - progression_pct
        
        # Cartes d'info stylées
        st.markdown(f"""
        <div style="background: linear-gradient(45deg, #FF6B6B, #4ECDC4); 
                    padding: 1rem; border-radius: 15px; margin: 0.5rem 0; 
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.2rem; font-weight: bold; color: white;">🏁 DISTANCE</span>
                <span style="font-size: 1.5rem; font-weight: bold; color: white;">{distance_parcourue:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(45deg, #4ECDC4, #45B7D1); 
                    padding: 1rem; border-radius: 15px; margin: 0.5rem 0; 
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.2rem; font-weight: bold; color: white;">🎯 RESTANT</span>
                <span style="font-size: 1.5rem; font-weight: bold; color: white;">{distance_restante:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Messages motivants selon la position avec style amélioré
        if progression_pct >= 100:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #F1C40F, #E67E22); 
                        padding: 1rem; border-radius: 15px; margin: 1rem 0; 
                        box-shadow: 0 10px 30px rgba(241, 196, 15, 0.4); 
                        border: 3px solid #F39C12; animation: pulse 2s infinite;">
                <h3 style="margin: 0; color: white; text-align: center;">🏆 VICTOIRE TOTALE ! 🏆</h3>
                <p style="margin: 0.5rem 0 0 0; color: white; text-align: center; font-weight: bold;">
                    Objectif dépassé ! Vous êtes un champion !
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif progression_pct >= 90:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #E74C3C, #C0392B); 
                        padding: 1rem; border-radius: 15px; margin: 1rem 0; 
                        box-shadow: 0 10px 30px rgba(231, 76, 60, 0.4);">
                <h3 style="margin: 0; color: white; text-align: center;">🔥 LIGNE DROITE ! 🔥</h3>
                <p style="margin: 0.5rem 0 0 0; color: white; text-align: center;">
                    Plus que quelques mètres vers la victoire !
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif progression_pct >= 75:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #9B59B6, #8E44AD); 
                        padding: 1rem; border-radius: 15px; margin: 1rem 0; 
                        box-shadow: 0 10px 30px rgba(155, 89, 182, 0.4);">
                <h3 style="margin: 0; color: white; text-align: center;">⚡ TURBO ACTIVÉ ! ⚡</h3>
                <p style="margin: 0.5rem 0 0 0; color: white; text-align: center;">
                    Excellent rythme ! Continuez !
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif progression_pct >= 50:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #3498DB, #2980B9); 
                        padding: 1rem; border-radius: 15px; margin: 1rem 0; 
                        box-shadow: 0 10px 30px rgba(52, 152, 219, 0.4);">
                <h3 style="margin: 0; color: white; text-align: center;">🏃 MI-PARCOURS ! 🏃</h3>
                <p style="margin: 0.5rem 0 0 0; color: white; text-align: center;">
                    Bonne progression ! Restez concentré !
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #95A5A6, #7F8C8D); 
                        padding: 1rem; border-radius: 15px; margin: 1rem 0; 
                        box-shadow: 0 10px 30px rgba(149, 165, 166, 0.4);">
                <h3 style="margin: 0; color: white; text-align: center;">🚀 DÉCOLLAGE ! 🚀</h3>
                <p style="margin: 0.5rem 0 0 0; color: white; text-align: center;">
                    Accélérez pour rattraper l'objectif !
                </p>
            </div>
            """, unsafe_allow_html=True)

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
