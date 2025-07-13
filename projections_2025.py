import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# --------- PARAMÈTRES GÉNÉRAUX ---------

# Mode clair/sombre manuel (peut être automatisé avec st.theme)
theme = st.sidebar.selectbox("Thème", ["Clair", "Sombre"])
if theme == "Clair":
    FONT_COLOR = "#0F1B2E"
    BG_COLOR = "#FFFFFF"
    ACCENT_COLOR = "#FFD700"
else:
    FONT_COLOR = "#FFD700"
    BG_COLOR = "#0F1B2E"
    ACCENT_COLOR = "#FFA500"

# --------- CSS ADAPTATIF ---------
st.markdown(f"""
    <style>
    :root {{
      --text-main-dark: #0F1B2E;
      --text-main-light: #FFD700;
      --background-dark: #0F1B2E;
      --background-light: #FFFFFF;
    }}
    body, .main-header, .metric-card, .insight-card, .section-title {{
      color: {FONT_COLOR};
    }}
    .main-header {{
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 25%, #FF8C00 50%, #FF6B35 75%, #E55100 100%);
        color: {FONT_COLOR};
        padding: 3rem 2rem;
        border-radius: 25px;
        margin: 1rem 0 3rem 0;
        text-align: center;
        box-shadow: 0 15px 35px rgba(255, 215, 0, 0.3);
        position: relative;
        overflow: hidden;
    }}
    .main-header h1 {{
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }}
    .main-header p {{
        font-size: 1.2rem;
        font-weight: 400;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }}
    .metric-card {{
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(15, 27, 46, 0.1);
        border: 2px solid transparent;
        background-clip: padding-box;
        margin-bottom: 2rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        color: {FONT_COLOR};
    }}
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #FFD700, #FFA500, #FF8C00, #FF6B35);
        border-radius: 20px 20px 0 0;
    }}
    .metric-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(255, 215, 0, 0.15);
        border-color: rgba(255, 215, 0, 0.3);
    }}
    .metric-card h3, .metric-card h2, .metric-card p {{
        color: {FONT_COLOR};
    }}
    .section-title {{
        color: {ACCENT_COLOR};
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1.5rem 0;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    .insight-card {{
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: {FONT_COLOR};
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3);
        transition: transform 0.3s ease;
    }}
    .insight-card:hover {{
        transform: translateY(-3px);
    }}
    .fade-in {{
        animation: fadeInUp 1s ease-out forwards;
    }}
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    .stDataFrame {{
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }}
    </style>
""", unsafe_allow_html=True)

# --------- CHARGEMENT DES DONNÉES ---------
@st.cache_data
def charger_projections():
    df = pd.read_excel("projections/Projections 2025.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower()
    return df

def afficher_jauge_animated(valeur_cible):
    gauge_placeholder = st.empty()
    valeur = 0
    step = max(1, int(valeur_cible / 40))
    while valeur < valeur_cible:
        valeur = min(valeur + step, valeur_cible)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = valeur,
            delta = {'reference': 100, 'increasing': {'color': "#28a745"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': ACCENT_COLOR},
                'bar': {'color': ACCENT_COLOR},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 2,
                'bordercolor': ACCENT_COLOR,
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(220, 53, 69, 0.3)'},
                    {'range': [50, 80], 'color': 'rgba(255, 193, 7, 0.3)'},
                    {'range': [80, 100], 'color': 'rgba(40, 167, 69, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            },
            title = {'text': "<b>Performance</b>", 'font': {'color': ACCENT_COLOR, 'size': 16}}
        ))
        fig_gauge.update_layout(
            height=300,
            paper_bgcolor=BG_COLOR,
            plot_bgcolor=BG_COLOR,
            font={'color': ACCENT_COLOR, 'family': "Poppins"}
        )
        gauge_placeholder.plotly_chart(fig_gauge, use_container_width=True)
        time.sleep(0.03)

def afficher_projections_2025():
    st.set_page_config(
        page_title="📈 Projections 2025 - BET-PLUS",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown(f"""
    <div class="main-header fade-in">
        <h1>📊 BET-PLUS | AUDET</h1>
        <h1>Projections des Inventaires 2025</h1>
        <p>Tableau de bord interactif pour le suivi de vos objectifs techniques</p>
    </div>
    """, unsafe_allow_html=True)

    df = charger_projections()

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
    realises_total = 31302
    progression_pct = (realises_total / objectif_total) * 100 if objectif_total else 0

    st.markdown('<h2 class="section-title">📊 Métriques de Performance</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3>🎯 Levés Techniques Réalisés</h3>
            <h2>{realises_total:,}</h2>
            <p>Total des inventaires effectués</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3>🏆 Objectif Technique 2025</h3>
            <h2>{objectif_total:,.0f}</h2>
            <p>Cible annuelle définie</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        couleur_prog = "#28a745" if progression_pct >= 100 else "#ffc107" if progression_pct >= 75 else "#dc3545"
        st.markdown(f"""
        <div class="metric-card fade-in">
            <h3>⚡ Taux de Réalisation</h3>
            <h2 style="color: {couleur_prog};">{progression_pct:.1f}%</h2>
            <p>Progression vers l'objectif</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">🚀 Progression Dynamique</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_progress = go.Figure()
        fig_progress.add_trace(go.Bar(
            y=['Progression'],
            x=[100],
            orientation='h',
            marker_color='rgba(108, 123, 138, 0.2)',
            showlegend=False,
            name='Objectif'
        ))
        fig_progress.add_trace(go.Bar(
            y=['Progression'],
            x=[min(progression_pct, 100)],
            orientation='h',
            marker_color='rgba(255, 215, 0, 0.9)',
            showlegend=False,
            name='Réalisé'
        ))
        fig_progress.add_annotation(
            x=progression_pct/2,
            y=0,
            text=f"<b>{progression_pct:.1f}%</b>",
            showarrow=False,
            font=dict(size=18, color=FONT_COLOR, family='Poppins'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor=ACCENT_COLOR,
            borderwidth=2
        )
        fig_progress.update_layout(
            title=dict(
                text="<b>Progression vers l'Objectif 2025</b>",
                font=dict(size=20, color=ACCENT_COLOR, family='Poppins')
            ),
            xaxis=dict(
                range=[0, 100],
                showgrid=False,
                showticklabels=True,
                tickfont=dict(color=ACCENT_COLOR),
                title=dict(text="Pourcentage (%)", font=dict(color=ACCENT_COLOR))
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False
            ),
            height=200,
            paper_bgcolor=BG_COLOR,
            plot_bgcolor=BG_COLOR,
            margin=dict(l=10, r=10, t=60, b=40)
        )
        st.plotly_chart(fig_progress, use_container_width=True)
    with col2:
        afficher_jauge_animated(progression_pct)

    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    if progression_pct >= 100:
        st.markdown('<div class="insight-card">🏆 <b>OBJECTIF ATTEINT !</b> Performance exceptionnelle de l\'équipe technique !</div>', unsafe_allow_html=True)
        st.balloons()
    elif progression_pct >= 90:
        st.markdown('<div class="insight-card">🔥 <b>EXCELLENT TRAVAIL !</b> Vous êtes dans la dernière ligne droite !</div>', unsafe_allow_html=True)
    elif progression_pct >= 75:
        st.markdown('<div class="insight-card">⚡ <b>TRÈS BONNE PROGRESSION !</b> Maintenez cette cadence technique !</div>', unsafe_allow_html=True)
    elif progression_pct >= 50:
        st.markdown('<div class="insight-card">🚀 <b>BON RYTHME !</b> Continuez vos efforts techniques !</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="insight-card">📈 <b>POTENTIEL D\'AMÉLIORATION</b> - Mobilisation nécessaire pour rattraper les objectifs</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">📊 Analyses Techniques Détaillées</h2>', unsafe_allow_html=True)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig_bar = go.Figure()
    colors_realises = [ACCENT_COLOR, "#FFA500", "#FF8C00", "#FF6B35", "#E55100"]
    colors_objectif = [FONT_COLOR, "#243B5C", "#2E4A71", "#385986", "#42689B"]
    fig_bar.add_trace(go.Bar(
        x=df["mois"],
        y=df["realises"],
        name="Inventaires Réalisés",
        marker_color=colors_realises[0],
        text=df["realises"],
        textposition='auto',
        textfont=dict(color=FONT_COLOR, size=12, family='Poppins'),
        hovertemplate='<b>%{x}</b><br>Réalisés: %{y:,}<br><extra></extra>',
        marker_line_color='white',
        marker_line_width=2
    ))
    fig_bar.add_trace(go.Bar(
        x=df["mois"],
        y=df["objectif_mensuel"],
        name="Objectif Technique",
        marker_color=colors_objectif[0],
        text=df["objectif_mensuel"],
        textposition='auto',
        textfont=dict(color=FONT_COLOR, size=12, family='Poppins'),
        hovertemplate='<b>%{x}</b><br>Objectif: %{y:,}<br><extra></extra>',
        marker_line_color='white',
        marker_line_width=2
    ))
    fig_bar.update_layout(
        title=dict(
            text="<b>Performance Mensuelle des Inventaires Techniques</b>",
            font=dict(size=20, color=FONT_COLOR, family='Poppins'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text="<b>Période</b>", font=dict(color=FONT_COLOR, size=14)),
            tickfont=dict(color=FONT_COLOR, size=12),
            gridcolor='rgba(26, 43, 71, 0.1)'
        ),
        yaxis=dict(
            title=dict(text="<b>Nombre d'Inventaires</b>", font=dict(color=FONT_COLOR, size=14)),
            tickfont=dict(color=FONT_COLOR, size=12),
            gridcolor='rgba(26, 43, 71, 0.1)'
        ),
        barmode='group',
        height=500,
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family="Poppins", color=FONT_COLOR),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(255,215,0,0.5)',
            borderwidth=1
        )
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=df["mois"],
        y=df["objectif_total"],
        fill='tozeroy',
        mode='lines+markers',
        name='Objectif Cumulé',
        line=dict(color=FONT_COLOR, width=4),
        fillcolor='rgba(26, 43, 71, 0.2)',
        marker=dict(size=8, color=FONT_COLOR, line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Objectif: %{y:,}<br><extra></extra>'
    ))
    fig_area.add_hline(
        y=realises_total,
        line_dash="dash",
        line_color=ACCENT_COLOR,
        line_width=4,
        annotation_text=f"<b>Réalisés: {realises_total:,}</b>",
        annotation_position="top right",
        annotation_font=dict(size=14, color=ACCENT_COLOR, family='Poppins')
    )
    fig_area.update_layout(
        title=dict(
            text="<b>Évolution Cumulative des Objectifs Techniques</b>",
            font=dict(size=20, color=FONT_COLOR, family='Poppins'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text="<b>Période</b>", font=dict(color=FONT_COLOR, size=14)),
            tickfont=dict(color=FONT_COLOR, size=12),
            gridcolor='rgba(26, 43, 71, 0.1)'
        ),
        yaxis=dict(
            title=dict(text="<b>Nombre d'Inventaires</b>", font=dict(color=FONT_COLOR, size=14)),
            tickfont=dict(color=FONT_COLOR, size=12),
            gridcolor='rgba(26, 43, 71, 0.1)'
        ),
        height=400,
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family="Poppins", color=FONT_COLOR)
    )
    st.plotly_chart(fig_area, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    df['perf_pct'] = (df['realises'] / df['objectif_mensuel'] * 100).fillna(0)
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=df['perf_pct'],
        theta=df['mois'],
        fill='toself',
        name='Performance Technique (%)',
        line=dict(color=ACCENT_COLOR, width=3),
        fillcolor='rgba(255, 215, 0, 0.3)',
        marker=dict(size=8, color=ACCENT_COLOR, line=dict(width=2, color='white'))
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(df['perf_pct'].max() * 1.1, 100)],
                tickfont=dict(color=FONT_COLOR, size=10),
                gridcolor='rgba(26, 43, 71, 0.2)'
            ),
            angularaxis=dict(
                tickfont=dict(color=FONT_COLOR, size=12, family='Poppins'),
                gridcolor='rgba(26, 43, 71, 0.2)'
            ),
            bgcolor=BG_COLOR
        ),
        title=dict(
            text="<b>Performance Technique par Période</b>",
            font=dict(size=20, color=FONT_COLOR, family='Poppins'),
            x=0.5
        ),
        height=500,
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family="Poppins", color=FONT_COLOR)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">📋 Données Techniques Détaillées</h2>', unsafe_allow_html=True)
    df_display = df.copy()
    df_display['Performance (%)'] = df_display['perf_pct'].round(1)
    df_display['Écart'] = df_display['realises'] - df_display['objectif_mensuel']
    df_display['realises'] = df_display['realises'].apply(lambda x: f"{x:,.0f}")
    df_display['objectif_mensuel'] = df_display['objectif_mensuel'].apply(lambda x: f"{x:,.0f}")
    df_display['objectif_total'] = df_display['objectif_total'].apply(lambda x: f"{x:,.0f}")
    df_display['Écart'] = df_display['Écart'].apply(lambda x: f"{x:+,.0f}")
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

    st.markdown('<h2 class="section-title">💡 Insights Techniques</h2>', unsafe_allow_html=True)
    mois_meilleur = df.loc[df['perf_pct'].idxmax(), 'mois']
    meilleure_perf = df['perf_pct'].max()
    moyenne_perf = df['perf_pct'].mean()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <div style="font-size: 1.2rem;">🏆 <b>Meilleure Performance</b></div>
            <div style="font-size: 1.5rem; margin-top: 0.5rem;">{mois_meilleur}: {meilleure_perf:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="insight-card">
            <div style="font-size: 1.2rem;">📊 <b>Performance Moyenne</b></div>
            <div style="font-size: 1.5rem; margin-top: 0.5rem;">{moyenne_perf:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        restant = max(0, objectif_total - realises_total)
        st.markdown(f"""
        <div class="insight-card">
            <div style="font-size: 1.2rem;">🎯 <b>Inventaires Restants</b></div>
            <div style="font-size: 1.5rem; margin-top: 0.5rem;">{restant:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">🔮 Prévisions et Recommandations</h2>', unsafe_allow_html=True)
    mois_restants = 12 - len(df)
    if mois_restants > 0:
        moyenne_mensuelle = realises_total / len(df)
        projection_fin_annee = realises_total + (moyenne_mensuelle * mois_restants)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📈 Projection Fin d'Année</h3>
                <h2>{projection_fin_annee:,.0f}</h2>
                <p>Basée sur la performance actuelle</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if projection_fin_annee >= objectif_total:
                st.success("✅ **Objectif projeté comme ATTEINT** avec la cadence actuelle !")
            else:
                deficit = objectif_total - projection_fin_annee
                st.warning(f"⚠️ **Risque de déficit** de {deficit:,.0f} inventaires avec la cadence actuelle")

    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.markdown("### 💡 Recommandations Stratégiques")
    if progression_pct < 50:
        st.markdown("""
        - 🚨 **Action immédiate requise** : Analyser les blocages opérationnels
        - 📋 **Révision des processus** : Optimiser les méthodes de levés techniques
        - 👥 **Renforcement des équipes** : Évaluer les besoins en personnel
        - 📊 **Suivi hebdomadaire** : Mettre en place des points de contrôle fréquents
        """)
    elif progression_pct < 75:
        st.markdown("""
        - ⚡ **Accélération nécessaire** : Intensifier le rythme des interventions
        - 🎯 **Focus sur l'efficacité** : Identifier les bonnes pratiques
        - 📈 **Monitoring renforcé** : Suivi bimensuel des performances
        - 🔧 **Optimisation continue** : Améliorer les outils et méthodes
        """)
    elif progression_pct < 90:
        st.markdown("""
        - 🔥 **Maintenir la cadence** : Excellente dynamique à préserver
        - 💪 **Motivation des équipes** : Communiquer sur les bons résultats
        - 📊 **Ajustements fins** : Peaufiner les derniers détails
        - 🎯 **Préparation de la fin d'année** : Anticiper les dernières échéances
        """)
    else:
        st.markdown("""
        - 🏆 **Performance exceptionnelle** : Félicitations à toute l'équipe !
        - 📈 **Capitalisation** : Documenter les bonnes pratiques
        - 🎯 **Nouveau défi** : Préparer les objectifs 2026
        - 🌟 **Reconnaissance** : Valoriser les efforts de l'équipe
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.markdown("### 📋 Informations Techniques")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📊 Source des données**")
        st.markdown("- Fichier: `Projections 2025.xlsx`")
        st.markdown("- Dernière mise à jour: Temps réel")
        st.markdown("- Fréquence: Mensuelle")
    with col2:
        st.markdown("**🎯 Indicateurs clés**")
        st.markdown("- Inventaires techniques réalisés")
        st.markdown("- Objectifs mensuels et cumulés")
        st.markdown("- Taux de performance")
    with col3:
        st.markdown("**🔧 Outils utilisés**")
        st.markdown("- Dashboard: Streamlit")
        st.markdown("- Graphiques: Plotly")
        st.markdown("- Analyse: Pandas")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">⚡ Actions Rapides</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔄 Actualiser les données"):
            st.rerun()
    with col2:
        if st.button("📊 Exporter le rapport"):
            st.info("Fonctionnalité d'export en cours de développement")
    with col3:
        if st.button("📧 Envoyer par email"):
            st.info("Fonctionnalité d'envoi en cours de développement")
    with col4:
        if st.button("📱 Partager"):
            st.info("Fonctionnalité de partage en cours de développement")

    if st.button("🎉 Message de motivation"):
        st.balloons()
        st.success("🌟 **Bravo à toute l'équipe BET-PLUS/AUDET !** Votre travail technique fait la différence ! 💪")

    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #6C7B8A; font-size: 0.9rem; margin-top: 2rem;">
        <p>📊 <b>BET-PLUS | AUDET</b> - Tableau de bord des projections techniques 2025</p>
        <p>Version 1.0 | Développé avec ❤️ pour l'équipe technique</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    afficher_projections_2025()
