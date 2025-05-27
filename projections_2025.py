import streamlit as st
import pandas as pd
import altair as alt
import time
import numpy as np

# Styles CSS pour animations modernes d'avancement
st.markdown("""
<style>
/* Barre de progression circulaire */
.circular-progress {
    position: relative;
    width: 120px;
    height: 120px;
    margin: 20px auto;
    border-radius: 50%;
    background: conic-gradient(from 0deg, #4CAF50 0%, #4CAF50 var(--progress), #e0e0e0 var(--progress), #e0e0e0 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
    animation: rotate 0.8s ease-in-out;
}

.circular-progress::before {
    content: '';
    position: absolute;
    width: 80px;
    height: 80px;
    background: white;
    border-radius: 50%;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
}

.progress-text {
    position: absolute;
    font-size: 16px;
    font-weight: bold;
    color: #2e7d32;
    z-index: 2;
}

@keyframes rotate {
    from { transform: rotate(-180deg); }
    to { transform: rotate(0deg); }
}

/* Barre de progression horizontale animée - AMÉLIORÉE */
.progress-bar-container {
    position: relative;
    width: 100%;
    height: 35px;
    background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: inset 0 3px 10px rgba(0,0,0,0.15);
    margin: 20px 0;
    border: 2px solid #e0e0e0;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 18px;
    position: relative;
    transition: width 2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    background: linear-gradient(45deg, 
        #4CAF50 0%, 
        #66BB6A 25%, 
        #81C784 50%, 
        #66BB6A 75%, 
        #4CAF50 100%);
    background-size: 200% 100%;
    animation: gradient-flow 3s ease-in-out infinite, pulse-glow 2s ease-in-out infinite;
    box-shadow: 0 2px 10px rgba(76, 175, 80, 0.4);
}

.progress-bar-fill::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(255,255,255,0.3) 30%, 
        rgba(255,255,255,0.6) 50%, 
        rgba(255,255,255,0.3) 70%, 
        transparent 100%);
    animation: shimmer-wave 2.5s infinite;
    border-radius: 18px;
}

.progress-bar-fill::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    right: 2px;
    height: 8px;
    background: linear-gradient(90deg, 
        rgba(255,255,255,0.6), 
        rgba(255,255,255,0.2));
    border-radius: 15px;
    animation: highlight-pulse 2s ease-in-out infinite;
}

@keyframes gradient-flow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

@keyframes shimmer-wave {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(200%); }
}

@keyframes pulse-glow {
    0%, 100% { 
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.4);
    }
    50% { 
        box-shadow: 0 4px 20px rgba(76, 175, 80, 0.8);
    }
}

@keyframes highlight-pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 0.9; }
}

/* Texte de progression amélioré */
.progress-label {
    color: #666;
    font-weight: 600;
    margin-bottom: 15px;
    font-size: 1.1em;
    text-align: center;
    animation: fade-in 1s ease-out;
}

.progress-value {
    color: #2e7d32;
    font-weight: bold;
    font-size: 20px;
    text-align: center;
    margin-top: 15px;
    animation: count-up 1.5s ease-out;
    text-shadow: 0 1px 3px rgba(46, 125, 50, 0.3);
}

@keyframes fade-in {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes count-up {
    from { opacity: 0; transform: scale(0.8); }
    to { opacity: 1; transform: scale(1); }
}

/* Indicateur de progression avec points */
.dots-progress {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    padding: 20px;
}

.dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #e0e0e0;
    transition: all 0.3s ease;
}

.dot.active {
    background: #4CAF50;
    transform: scale(1.2);
    box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
    animation: pulse-dot 1.5s infinite;
}

@keyframes pulse-dot {
    0%, 100% { transform: scale(1.2); }
    50% { transform: scale(1.4); }
}

/* Carte de métrique animée */
.metric-card {
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    border: 1px solid #e9ecef;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.1), transparent);
    animation: sweep 3s infinite;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(76, 175, 80, 0.2);
}

@keyframes sweep {
    0% { left: -100%; }
    100% { left: 100%; }
}

.metric-value {
    font-size: 2.5em;
    font-weight: bold;
    color: #2e7d32;
    margin: 10px 0;
    animation: count-up 1s ease-out;
}

.metric-label {
    color: #666;
    font-size: 1.1em;
    margin-bottom: 15px;
}

/* Indicateur de statut avec icônes */
.status-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    font-weight: 600;
    transition: all 0.3s ease;
}

.status-excellent {
    background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
    color: #2e7d32;
    border-left: 4px solid #4caf50;
}

.status-good {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    color: #f57c00;
    border-left: 4px solid #ff9800;
}

.status-warning {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    color: #c62828;
    border-left: 4px solid #f44336;
}

.icon {
    font-size: 1.5em;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-5px); }
    60% { transform: translateY(-3px); }
}

/* Section d'état d'avancement */
.progress-section {
    background: linear-gradient(135deg, #f8f9fa, #ffffff);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 1px solid #e9ecef;
}

.section-title {
    text-align: center;
    color: #2e7d32;
    font-size: 1.8em;
    font-weight: bold;
    margin-bottom: 30px;
    animation: slide-down 1s ease-out;
}

@keyframes slide-down {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def charger_projections():
    df = pd.read_excel("projections/Projections 2025.xlsx", engine="openpyxl")
    # Nettoyage des noms de colonnes
    df.columns = df.columns.str.strip().str.lower()
    return df

def create_circular_progress(percentage, text, label=""):
    """Crée une barre de progression circulaire"""
    progress_deg = min(percentage * 3.6, 360)  # Convertir en degrés
    
    html = f"""
    <div style="text-align: center;">
        <div style="color: #666; font-weight: 600; margin-bottom: 10px;">{label}</div>
        <div class="circular-progress" style="--progress: {progress_deg}deg;">
            <div class="progress-text">{text}</div>
        </div>
    </div>
    """
    return html

def create_horizontal_progress(percentage, text, label=""):
    """Crée une barre de progression horizontale améliorée"""
    width = min(percentage, 100)
    
    html = f"""
    <div>
        <div class="progress-label">{label}</div>
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {width}%;">
            </div>
        </div>
        <div class="progress-value">{text}</div>
    </div>
    """
    return html

def create_dots_progress(percentage, total_dots=10):
    """Crée un indicateur de progression avec des points"""
    active_dots = int((percentage / 100) * total_dots)
    
    dots_html = ""
    for i in range(total_dots):
        dot_class = "dot active" if i < active_dots else "dot"
        dots_html += f'<div class="{dot_class}"></div>'
    
    html = f"""
    <div class="dots-progress">
        {dots_html}
    </div>
    <div style="text-align: center; color: #2e7d32; font-weight: bold;">
        {percentage:.1f}% Complete
    </div>
    """
    return html

def create_metric_card(title, value, subtitle, percentage):
    """Crée une carte métrique animée"""
    
    # Déterminer le statut
    if percentage >= 90:
        status_class = "status-excellent"
        icon = "🎯"
    elif percentage >= 70:
        status_class = "status-good"
        icon = "⚡"
    else:
        status_class = "status-warning"
        icon = "⚠️"
    
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="status-indicator {status_class}">
            <span class="icon">{icon}</span>
            <span>{subtitle}</span>
        </div>
    </div>
    """
    return html

def afficher_projections_2025():
    st.header("📅 Projections des Inventaires - 2025")
    
    # Choix du style d'animation
    col_choice, col_empty = st.columns([1, 2])
    with col_choice:
        animation_style = st.selectbox(
            "🎨 Style d'animation",
            ["Barres horizontales", "Cercles", "Points", "Cartes métriques"],
            index=0  # Barres horizontales par défaut
        )
    
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
            if cle in col.lower():
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
    realises_total = 23693
    progression_pct = (realises_total / objectif_total) * 100 if objectif_total else 0
    
    # Calculs pour les métriques
    mois_ecoules = len(df)
    moyenne_mensuelle = realises_total / mois_ecoules if mois_ecoules > 0 else 0
    objectif_mensuel_moyen = df["objectif_mensuel"].mean()
    pourcentage_mensuel = (moyenne_mensuelle / objectif_mensuel_moyen * 100) if objectif_mensuel_moyen > 0 else 0
    
    projection_annuelle = (realises_total / mois_ecoules) * 12 if mois_ecoules > 0 else 0
    pct_projection = (projection_annuelle / objectif_total * 100) if objectif_total > 0 else 0
    
    # Section État d'avancement avec animation
    st.markdown("""
    <div class="progress-section">
        <div class="section-title">🚀 État d'avancement</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Affichage selon le style choisi
    if animation_style == "Cartes métriques":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                create_metric_card(
                    "🎯 Objectif Global",
                    f"{realises_total:,}",
                    f"{progression_pct:.1f}% atteint",
                    progression_pct
                ),
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                create_metric_card(
                    "📈 Moyenne Mensuelle",
                    f"{moyenne_mensuelle:,.0f}",
                    f"{pourcentage_mensuel:.1f}% de l'objectif",
                    pourcentage_mensuel
                ),
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                create_metric_card(
                    "🔮 Projection Annuelle",
                    f"{projection_annuelle:,.0f}",
                    f"{pct_projection:.1f}% projeté",
                    pct_projection
                ),
                unsafe_allow_html=True
            )
    
    else:
        col1, col2, col3 = st.columns(3)
        
        if animation_style == "Barres horizontales":
            with col1:
                st.markdown(
                    create_horizontal_progress(
                        progression_pct, 
                        f"{progression_pct:.1f}% • {realises_total:,}/{objectif_total:,}", 
                        "🎯 Objectif Global"
                    ),
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(
                    create_horizontal_progress(
                        pourcentage_mensuel, 
                        f"{pourcentage_mensuel:.1f}% • {moyenne_mensuelle:,.0f}/mois", 
                        "📊 Moyenne Mensuelle"
                    ),
                    unsafe_allow_html=True
                )
            
            with col3:
                st.markdown(
                    create_horizontal_progress(
                        pct_projection, 
                        f"{pct_projection:.1f}% • {projection_annuelle:,.0f}", 
                        "🔮 Projection Annuelle"
                    ),
                    unsafe_allow_html=True
                )
        
        elif animation_style == "Cercles":
            with col1:
                st.markdown(
                    create_circular_progress(
                        progression_pct, 
                        f"{progression_pct:.1f}%", 
                        "🎯 Objectif Global"
                    ),
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(
                    create_circular_progress(
                        pourcentage_mensuel, 
                        f"{pourcentage_mensuel:.1f}%", 
                        "📊 Moyenne Mensuelle"
                    ),
                    unsafe_allow_html=True
                )
            
            with col3:
                st.markdown(
                    create_circular_progress(
                        pct_projection, 
                        f"{pct_projection:.1f}%", 
                        "🔮 Projection"
                    ),
                    unsafe_allow_html=True
                )
        
        elif animation_style == "Points":
            with col1:
                st.markdown("**🎯 Objectif Global**")
                st.markdown(create_dots_progress(progression_pct), unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📊 Moyenne Mensuelle**")
                st.markdown(create_dots_progress(pourcentage_mensuel), unsafe_allow_html=True)
            
            with col3:
                st.markdown("**🔮 Projection**")
                st.markdown(create_dots_progress(pct_projection), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Remplacez la section du graphique mensuel par ce code plus stylé
    st.markdown("---")
    st.subheader("🎯 Performance Mensuelle - Levées Réalisées vs Objectif")

    # Préparation des données pour le graphique stylé
    objectif_mensuel_fixe = 8000
    df_chart = df[["mois", "realises"]].copy()
    df_chart["objectif"] = objectif_mensuel_fixe
    df_chart["pourcentage_atteint"] = (df_chart["realises"] / objectif_mensuel_fixe * 100).round(1)
    df_chart["statut"] = df_chart["pourcentage_atteint"].apply(
        lambda x: "🎯 Objectif atteint" if x >= 100 
                 else "⚡ En progression" if x >= 75 
                 else "⚠️ À améliorer"
    )

    # Graphique en aires empilées avec ligne d'objectif
    base = alt.Chart(df_chart).add_selection(
        alt.selection_single(fields=['mois'])
    )

    # Zone des réalisations avec dégradé
    area_realises = base.mark_area(
        opacity=0.7,
        color=alt.expr("datum.realises >= 8000 ? '#4CAF50' : '#FF9800'"),
        interpolate='monotone'
    ).encode(
        x=alt.X('mois:N', 
                title='Mois', 
                sort=list(df["mois"]),
                axis=alt.Axis(labelAngle=-45, labelFontSize=12)),
        y=alt.Y('realises:Q', 
                title='Nombre de levées',
                scale=alt.Scale(domain=[0, max(df_chart["realises"].max(), objectif_mensuel_fixe) * 1.1])),
        tooltip=[
            alt.Tooltip('mois:N', title='Mois'),
            alt.Tooltip('realises:Q', title='Levées réalisées', format=','),
            alt.Tooltip('pourcentage_atteint:Q', title='% Objectif atteint', format='.1f'),
            alt.Tooltip('statut:N', title='Statut')
        ]
    )

    # Ligne d'objectif avec style
    ligne_objectif = alt.Chart(pd.DataFrame({
        'mois': df_chart['mois'],
        'objectif': [objectif_mensuel_fixe] * len(df_chart)
    })).mark_line(
        color='red',
        strokeWidth=3,
        strokeDash=[8, 4]
    ).encode(
        x=alt.X('mois:N', sort=list(df["mois"])),
        y='objectif:Q'
    )

    # Points sur la ligne des réalisations
    points_realises = base.mark_circle(
        size=150,
        stroke='white',
        strokeWidth=2
    ).encode(
        x=alt.X('mois:N', sort=list(df["mois"])),
        y='realises:Q',
        color=alt.Color(
            'statut:N',
            scale=alt.Scale(
                domain=["🎯 Objectif atteint", "⚡ En progression", "⚠️ À améliorer"],
                range=["#4CAF50", "#FF9800", "#f44336"]
            ),
            legend=alt.Legend(title="Performance", orient="top")
        ),
        tooltip=[
            alt.Tooltip('mois:N', title='Mois'),
            alt.Tooltip('realises:Q', title='Levées réalisées', format=','),
            alt.Tooltip('pourcentage_atteint:Q', title='% Objectif atteint', format='.1f'),
            alt.Tooltip('statut:N', title='Statut')
        ]
    )

    # Texte pour la ligne d'objectif
    text_objectif = alt.Chart(pd.DataFrame({
        'x': [df_chart['mois'].iloc[-1]],
        'y': [objectif_mensuel_fixe + 200],
        'text': [f'Objectif: {objectif_mensuel_fixe:,}']
    })).mark_text(
        align='right',
        fontSize=12,
        fontWeight='bold',
        color='red'
    ).encode(
        x='x:N',
        y='y:Q',
        text='text:N'
    )

    # Assemblage du graphique final
    graphique_final = (area_realises + ligne_objectif + points_realises + text_objectif).resolve_scale(
        color='independent'
    ).properties(
        height=450,
        title=alt.TitleParams(
            text="Performance mensuelle des levées d'inventaire",
            fontSize=16,
            anchor='start',
            color='#2e7d32'
        )
    )

    st.altair_chart(graphique_final, use_container_width=True)

    # Résumé statistique stylé
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    mois_objectif_atteint = len(df_chart[df_chart["pourcentage_atteint"] >= 100])
    meilleur_mois = df_chart.loc[df_chart["realises"].idxmax()]
    moyenne_realises = df_chart["realises"].mean()
    ecart_moyen_objectif = ((moyenne_realises - objectif_mensuel_fixe) / objectif_mensuel_fixe * 100)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏆 Mois réussis</div>
            <div class="metric-value">{mois_objectif_atteint}</div>
            <div style="color: #666;">sur {len(df_chart)} mois</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⭐ Meilleur mois</div>
            <div class="metric-value">{meilleur_mois['realises']:,.0f}</div>
            <div style="color: #666;">{meilleur_mois['mois']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📊 Moyenne</div>
            <div class="metric-value">{moyenne_realises:,.0f}</div>
            <div style="color: #666;">levées/mois</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        couleur_ecart = "#4CAF50" if ecart_moyen_objectif >= 0 else "#f44336"
        signe_ecart = "+" if ecart_moyen_objectif >= 0 else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📈 Écart moyen</div>
            <div class="metric-value" style="color: {couleur_ecart};">{signe_ecart}{ecart_moyen_objectif:.1f}%</div>
            <div style="color: #666;">vs objectif</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📈 Évolution de l'objectif cumulé")
    
    area_chart = alt.Chart(df).mark_area(opacity=0.3, color="lightblue").encode(
        x=alt.X("mois:N", title="Mois", sort=list(df["mois"])),
        y=alt.Y("objectif_total:Q", title="Objectif Cumulé"),
        tooltip=["mois:N", "objectif_total:Q"]
    ).properties(height=350)
    
    ligne_levés = alt.Chart(pd.DataFrame({
        "y": [realises_total],
        "text": ["Levés actuels"]
    })).mark_rule(color='green', strokeDash=[4, 4]).encode(
        y='y:Q'
    ) + alt.Chart(pd.DataFrame({
        "y": [realises_total],
        "text": [f"↳ {realises_total:,} levés"]
    })).mark_text(align="left", dx=5, dy=-5, color="green").encode(
        y="y:Q",
        text="text:N"
    )
    
    st.altair_chart(area_chart + ligne_levés, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📋 Données complètes")
    st.dataframe(df, use_container_width=True)

# Appel de la fonction principale
if __name__ == "__main__":
    afficher_projections_2025()
