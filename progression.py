import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time


def afficher_etat_avancement(df_etapes=None):
    """
    Fonction principale pour afficher l'onglet État d'avancement des communes
    avec un design modernisé et des animations
    """
    # CSS personnalisé pour le design moderne
    st.markdown("""
    <style>
    /* Style général */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        animation: slideDown 0.8s ease-out;
    }
    
    @keyframes slideDown {
        from { transform: translateY(-50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    @keyframes fadeInUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .progress-ring {
        transform: rotate(-90deg);
        animation: rotate 2s ease-in-out;
    }
    
    @keyframes rotate {
        from { transform: rotate(-90deg) scale(0.8); }
        to { transform: rotate(-90deg) scale(1); }
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-radius: 10px;
        transition: all 0.3s ease;
        animation: fadeIn 0.8s ease-out;
    }
    
    .legend-item:hover {
        background: rgba(102, 126, 234, 0.1);
        transform: translateX(5px);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .section-header {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(240, 147, 251, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(240, 147, 251, 0); }
        100% { box-shadow: 0 0 0 0 rgba(240, 147, 251, 0); }
    }
    
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
        animation: bounceIn 0.5s ease-out;
    }
    
    @keyframes bounceIn {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: slideInRight 0.6s ease-out;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

    # En-tête principal avec animation
    st.markdown("""
    <div class="main-header">
        <h1>📅 État d'avancement des communes</h1>
        <p>Tableau de bord interactif pour le suivi des opérations foncières</p>
    </div>
    """, unsafe_allow_html=True)

    # Simulation de chargement avec spinner
    with st.spinner("🔄 Chargement des données..."):
        time.sleep(0.5)  # Simulation du temps de chargement
        
        # Chargement des données
        if df_etapes is None:
            df_etapes = charger_donnees_etapes()
        else:
            if "Progrès (%)" not in df_etapes.columns:
                df_etapes["Progrès (%)"] = df_etapes["Progrès des étapes"].apply(evaluer_progres)

    # Interface de filtrage modernisée
    region_sel, commune_sel, csig_sel, df_etapes_filtre = filtrer_donnees_moderne(df_etapes)

    # Afficher la légende modernisée
    afficher_legende_moderne()

    # Afficher le contenu selon les filtres
    if region_sel == "Toutes" and commune_sel == "Toutes" and csig_sel == "Tous":
        afficher_vue_globale_moderne(df_etapes)
    elif region_sel != "Toutes" and commune_sel == "Toutes" and csig_sel == "Tous":
        afficher_vue_region_moderne(df_etapes_filtre, region_sel)
    else:
        afficher_details_communes_moderne(df_etapes_filtre)


@st.cache_data
def charger_donnees_etapes():
    """
    Charge et prépare les données d'état d'avancement
    """
    try:
        df_etapes = pd.read_excel("data/Etat des opérations Boundou-Mai 2025.xlsx", engine="openpyxl")
        df_etapes.fillna("", inplace=True)
        df_etapes["Progrès (%)"] = df_etapes["Progrès des étapes"].apply(evaluer_progres)
        return df_etapes
    except FileNotFoundError:
        st.error("Le fichier 'data/Etat des opérations Boundou-Mai 2025.xlsx' n'a pas été trouvé.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return pd.DataFrame()


def evaluer_progres(etapes):
    """
    Évalue le progrès d'une commune basé sur les étapes décrites
    """
    if etapes is None or pd.isna(etapes) or not isinstance(etapes, str):
        return 0.0
    
    if etapes.strip() == "":
        return 0.0
    
    total = 4
    score = 0
    
    try:
        etapes_list = [e.strip().lower() for e in etapes.split("\n") if e.strip() != ""]
        
        for etape in etapes_list:
            if "complét" in etape or "affichage public (complétés)" in etape:
                score += 1
            elif "en cours" in etape or "débuté" in etape or "commencé" in etape:
                score += 0.5
        
        return (score / total) * 100
    
    except Exception as e:
        print(f"Error processing etapes: {etapes}, Error: {e}")
        return 0.0


def filtrer_donnees_moderne(df_etapes):
    """
    Interface de filtrage modernisée avec animations
    """
    if df_etapes.empty:
        return "Toutes", "Toutes", "Tous", df_etapes
    
    st.markdown('<div class="section-header"><h3>🎯 Filtres de sélection</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "Région" in df_etapes.columns:
            regions = ["Toutes"] + sorted(df_etapes["Région"].dropna().unique())
            region_sel = st.selectbox("🌍 Région", regions, key="region_filter")
        else:
            st.error("Colonne 'Région' manquante")
            region_sel = "Toutes"
    
    df_etapes_filtre = df_etapes if region_sel == "Toutes" else df_etapes[df_etapes["Région"] == region_sel]
    
    with col2:
        if "Commune" in df_etapes.columns:
            communes = ["Toutes"] + sorted(df_etapes_filtre["Commune"].unique())
            commune_sel = st.selectbox("🏘️ Commune", communes, key="commune_filter")
        else:
            st.error("Colonne 'Commune' manquante")
            commune_sel = "Toutes"
    
    df_etapes_filtre = df_etapes_filtre if commune_sel == "Toutes" else df_etapes_filtre[
        df_etapes_filtre["Commune"] == commune_sel]
    
    with col3:
        if "CSIG" in df_etapes.columns:
            csigs = ["Tous"] + sorted(df_etapes_filtre["CSIG"].unique())
            csig_sel = st.selectbox("📌 CSIG", csigs, key="csig_filter")
        else:
            st.error("Colonne 'CSIG' manquante")
            csig_sel = "Tous"
    
    df_etapes_filtre = df_etapes_filtre if csig_sel == "Tous" else df_etapes_filtre[
        df_etapes_filtre["CSIG"] == csig_sel]

    return region_sel, commune_sel, csig_sel, df_etapes_filtre


def afficher_legende_moderne():
    """
    Affiche une légende modernisée avec animations
    """
    st.markdown('<div class="section-header"><h3>🎨 Légende des indicateurs</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    legendes = [
        ("🔴", "0-25%", "Non commencé", "#FF6B6B"),
        ("🟠", "25-50%", "En cours", "#FF9500"),
        ("🟡", "50-75%", "En cours avancé", "#FFD93D"),
        ("🟢", "75-100%", "Près de la fin", "#6BCF7F")
    ]
    
    for i, (icon, range_val, status, color) in enumerate(legendes):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div class="legend-item" style="background: linear-gradient(45deg, {color}20, {color}10);">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <div>
                    <strong>{range_val}</strong><br>
                    <small>{status}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)


def afficher_vue_globale_moderne(df_etapes):
    """
    Affiche une vue globale modernisée avec animations
    """
    st.markdown('<div class="section-header"><h2>📊 Tableau de bord global</h2></div>', unsafe_allow_html=True)

    if df_etapes.empty:
        st.warning("Aucune donnée disponible")
        return

    # Calculer les statistiques
    communes_debutees = df_etapes[df_etapes["Progrès (%)"] > 0]
    pourcentage_debutees = (len(communes_debutees) / len(df_etapes)) * 100 if len(df_etapes) > 0 else 0
    progres_moyen = df_etapes["Progrès (%)"].mean()

    # Cartes métriques modernisées
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("📍", "Total communes", len(df_etapes), "#667eea"),
        ("🚀", "Communes débutées", len(communes_debutees), "#f093fb"),
        ("📊", "Taux de démarrage", f"{pourcentage_debutees:.1f}%", "#4ecdc4"),
        ("⭐", "Progrès moyen", f"{progres_moyen:.1f}%", "#45b7d1")
    ]
    
    for i, (icon, title, value, color) in enumerate(metrics):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color}; animation-delay: {i*0.2}s;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h4 style="margin: 0; color: {color};">{title}</h4>
                        <h2 style="margin: 0.5rem 0; color: #2c3e50;">{value}</h2>
                    </div>
                    <div style="font-size: 2rem; opacity: 0.7;">{icon}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Graphiques avec animations
    afficher_graphiques_modernises(df_etapes)


def afficher_graphiques_modernises(df_etapes):
    """
    Affiche des graphiques modernisés avec animations
    """
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique d'avancement par région
        if "Région" in df_etapes.columns:
            region_progress = df_etapes.groupby("Région")["Progrès (%)"].mean().reset_index()
            
            fig_regions = px.bar(
                region_progress,
                x="Région",
                y="Progrès (%)",
                title="🌍 Progression par région",
                color="Progrès (%)",
                color_continuous_scale=["#FF6B6B", "#FF9500", "#FFD93D", "#6BCF7F"],
                template="plotly_white"
            )
            
            fig_regions.update_layout(
                height=400,
                title_font_size=16,
                title_x=0.5,
                showlegend=False,
                xaxis_title="Région",
                yaxis_title="Progrès (%)",
                yaxis=dict(range=[0, 100])
            )
            
            fig_regions.update_traces(
                hovertemplate="<b>%{x}</b><br>Progrès: %{y:.1f}%<extra></extra>",
                texttemplate="%{y:.1f}%",
                textposition="outside"
            )
            
            st.plotly_chart(fig_regions, use_container_width=True)
    
    with col2:
        # Graphique en secteurs modernisé
        df_etapes["Catégorie"] = pd.cut(
            df_etapes["Progrès (%)"],
            bins=[0, 0.1, 25, 50, 75, 100],
            labels=["Non débutées", "Débutées", "En cours", "Avancées", "Terminées"]
        )
        
        resume = df_etapes["Catégorie"].value_counts().reset_index()
        resume.columns = ["État", "Nombre"]
        
        fig_pie = px.pie(
            resume,
            values="Nombre",
            names="État",
            title="📈 Répartition des états",
            color_discrete_map={
                "Non débutées": "#FF6B6B",
                "Débutées": "#FF9500",
                "En cours": "#FFD93D",
                "Avancées": "#6BCF7F",
                "Terminées": "#4ECDC4"
            },
            template="plotly_white"
        )
        
        fig_pie.update_layout(
            height=400,
            title_font_size=16,
            title_x=0.5
        )
        
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Nombre: %{value}<br>Pourcentage: %{percent}<extra></extra>"
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)


def afficher_vue_region_moderne(df_etapes_filtre, region_sel):
    """
    Affiche une vue région modernisée
    """
    st.markdown(f'<div class="section-header"><h2>🌍 Région: {region_sel}</h2></div>', unsafe_allow_html=True)

    if df_etapes_filtre.empty:
        st.warning(f"Aucune donnée pour la région {region_sel}")
        return

    # Statistiques de la région
    communes_region = len(df_etapes_filtre)
    communes_debutees = len(df_etapes_filtre[df_etapes_filtre["Progrès (%)"] > 0])
    progres_moyen = df_etapes_filtre["Progrès (%)"].mean()

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏘️ Communes", communes_region)
    with col2:
        st.metric("🚀 Débutées", communes_debutees)
    with col3:
        st.metric("📊 Progrès moyen", f"{progres_moyen:.1f}%")

    # Tableau des communes avec design moderne
    afficher_tableau_moderne(df_etapes_filtre, region_sel)


def afficher_tableau_moderne(df_etapes_filtre, region_sel):
    """
    Affiche un tableau modernisé des communes
    """
    colonnes = ["Commune", "CSIG", "Progrès (%)"]
    if "Date Début" in df_etapes_filtre.columns:
        colonnes.append("Date Début")
    
    resume = df_etapes_filtre[colonnes].copy()
    resume["État"] = resume["Progrès (%)"].apply(get_progress_indicator_moderne)
    resume = resume.sort_values("Progrès (%)", ascending=False)
    
    st.dataframe(
        resume,
        use_container_width=True,
        height=400,
        column_config={
            "Progrès (%)": st.column_config.ProgressColumn(
                "Progrès",
                help="Pourcentage d'avancement",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "État": st.column_config.TextColumn(
                "État",
                help="État d'avancement",
                width="medium",
            )
        }
    )


def get_progress_indicator_moderne(progress):
    """
    Retourne un indicateur moderne du progrès
    """
    if progress < 0.1:
        return "🔴 Non débuté"
    elif progress < 25:
        return "🟠 Débuté"
    elif progress < 50:
        return "🟡 En cours"
    elif progress < 75:
        return "🟢 Avancé"
    else:
        return "✅ Terminé"


def afficher_details_communes_moderne(df_etapes_filtre):
    """
    Affiche les détails des communes avec un design moderne
    """
    if len(df_etapes_filtre) == 0:
        st.warning("Aucune commune trouvée")
        return

    for idx, row in df_etapes_filtre.iterrows():
        progress = row["Progrès (%)"]
        
        # Conteneur principal avec effet glassmorphism
        with st.container():
            st.markdown(f"""
            <div class="glass-card">
                <h3 style="color: #667eea; margin-bottom: 1rem;">
                    🏘️ {row['Commune']} - 📌 {row['CSIG']}
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Jauge de progrès modernisée
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=progress,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Progrès", "font": {"size": 16}},
                    delta={"reference": 100, "suffix": "%"},
                    gauge={
                        "axis": {"range": [None, 100], "tickwidth": 1},
                        "bar": {"color": get_color_for_progress(progress)},
                        "bgcolor": "white",
                        "borderwidth": 2,
                        "bordercolor": "gray",
                        "steps": [
                            {"range": [0, 25], "color": "rgba(255, 107, 107, 0.3)"},
                            {"range": [25, 50], "color": "rgba(255, 149, 0, 0.3)"},
                            {"range": [50, 75], "color": "rgba(255, 217, 61, 0.3)"},
                            {"range": [75, 100], "color": "rgba(107, 207, 127, 0.3)"}
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 90
                        }
                    }
                ))
                
                fig.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=50, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#2c3e50", "family": "Arial"}
                )
                
                st.plotly_chart(fig, use_container_width=True, key=f"gauge_{idx}")
            
            with col2:
                # Informations détaillées
                afficher_infos_moderne(row)
        
        st.markdown("---")


def get_color_for_progress(progress):
    """
    Retourne la couleur appropriée selon le progrès
    """
    if progress < 25:
        return "#FF6B6B"
    elif progress < 50:
        return "#FF9500"
    elif progress < 75:
        return "#FFD93D"
    else:
        return "#6BCF7F"


def afficher_infos_moderne(row):
    """
    Affiche les informations d'une commune de manière moderne
    """
    start_date = row.get("Date Début", "Non spécifiée")
    end_date = row.get("Date de prévision de compléter les inventaires fonciers", "Non spécifiée")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea20, #764ba220); 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <p><strong>📅 Début:</strong> {start_date}</p>
        <p><strong>🎯 Fin prévue:</strong> {end_date}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 🔄 Progression des étapes")
    
    etapes_raw = row.get("Progrès des étapes", "")
    if etapes_raw is None or pd.isna(etapes_raw) or not isinstance(etapes_raw, str):
        etapes = ["Non spécifié"] * 4
    else:
        etapes = etapes_raw.split("\n")
    
    etapes_noms = [
        "1. Levés topo et enquêtes",
        "2. Affichage public",
        "3. Réunion du CTASF",
        "4. Délibération"
    ]
    
    for i, nom in enumerate(etapes_noms):
        status = etapes[i] if i < len(etapes) else "Non spécifié"
        status_lower = status.lower()
        
        if "complét" in status_lower:
            icon = "✅"
            color = "#6BCF7F"
        elif "en cours" in status_lower:
            icon = "🔄"
            color = "#FFD93D"
        else:
            icon = "⭕"
            color = "#FF6B6B"
        
        st.markdown(f"""
        <div class="status-badge" style="background: {color}20; color: {color}; border: 1px solid {color}40;">
            {icon} <strong>{nom}</strong>: {status}
        </div>
        """, unsafe_allow_html=True)


# Fonction de compatibilité
def afficher_progression(df_etapes=None):
    """
    Fonction de compatibilité pour l'appel depuis dashboard.py
    """
    afficher_etat_avancement(df_etapes)
