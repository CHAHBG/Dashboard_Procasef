import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# CSS personnalisé pour un look moderne
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .metric-card p {
        margin: 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .metric-card-female {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .metric-card-male {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .metric-card-total {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    .ratio-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    .filter-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
    }
    
    .section-header {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def charger_donnees_genre():
    """Chargement des données avec gestion d'erreurs"""
    try:
        df_genre_trimestre = pd.read_excel("genre/Genre par trimestre.xlsx", engine="openpyxl")
        df_repartition_genre = pd.read_excel("genre/Repartition genre.xlsx", engine="openpyxl")
        df_genre_commune = pd.read_excel("genre/Genre par Commune.xlsx", engine="openpyxl")
        return df_genre_trimestre, df_repartition_genre, df_genre_commune
    except FileNotFoundError as e:
        st.error(f"Fichiers de données non trouvés: {e}")
        st.info("Veuillez vérifier que les fichiers suivants existent:")
        st.info("- genre/Genre par trimestre.xlsx")
        st.info("- genre/Repartition genre.xlsx") 
        st.info("- genre/Genre par Commune.xlsx")
        return None, None, None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None, None, None

def create_modern_metric_card(title, value, color_class=""):
    """Création d'une carte métrique moderne"""
    return f"""
    <div class="metric-card {color_class}">
        <h3>{value:,}</h3>
        <p>{title}</p>
    </div>
    """

def create_gauge_chart(percentage, title, target=30):
    """Création d'un graphique en jauge moderne"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 24, 'color': '#2c3e50'}},
        delta = {'reference': target, 'increasing': {'color': "#27ae60"}, 'decreasing': {'color': "#e74c3c"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#f39c12"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, target], 'color': '#ffebee'},
                {'range': [target, 100], 'color': '#e8f5e8'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        font={'color': "#2c3e50", 'family': "Arial"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_modern_pie_chart(data, names, values, title, colors=None):
    """Création d'un graphique en secteurs moderne"""
    if colors is None:
        colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60']
    
    fig = px.pie(
        data, 
        names=names, 
        values=values,
        title=title,
        color_discrete_sequence=colors,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Nombre: %{value:,}<br>Pourcentage: %{percent}<extra></extra>',
        pull=[0.1 if i == 0 else 0 for i in range(len(data))]
    )
    
    fig.update_layout(
        font=dict(size=14, color='#2c3e50'),
        title_font=dict(size=20, color='#2c3e50'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def create_modern_bar_chart(data, x, y, color, title, color_map=None):
    """Création d'un graphique en barres moderne"""
    fig = px.bar(
        data, 
        x=x, 
        y=y, 
        color=color,
        title=title,
        color_discrete_map=color_map,
        text=y
    )
    
    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:,}<extra></extra>'
    )
    
    fig.update_layout(
        font=dict(size=12, color='#2c3e50'),
        title_font=dict(size=18, color='#2c3e50'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="",
        yaxis_title="Nombre de personnes",
        showlegend=True
    )
    return fig

def create_stacked_bar_chart(data, x, y, color, title, color_map=None):
    """Création d'un graphique en barres empilées"""
    fig = px.bar(
        data, 
        x=x, 
        y=y, 
        color=color,
        title=title,
        color_discrete_map=color_map,
        barmode='stack'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:,}<extra></extra>'
    )
    
    fig.update_layout(
        font=dict(size=12, color='#2c3e50'),
        title_font=dict(size=18, color='#2c3e50'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        xaxis_title="",
        yaxis_title="Nombre de personnes",
        xaxis_tickangle=-45,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def create_area_chart(data, x, y_cols, title, color_map=None):
    """Création d'un graphique en aires"""
    fig = px.area(
        data, 
        x=x, 
        y=y_cols,
        title=title,
        color_discrete_map=color_map,
        markers=True
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:,}<extra></extra>'
    )
    
    fig.update_layout(
        font=dict(size=12, color='#2c3e50'),
        title_font=dict(size=18, color='#2c3e50'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Période",
        yaxis_title="Nombre de personnes",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def afficher_repartition_genre():
    """Fonction principale pour afficher l'analyse genre (appelée depuis dashboard.py)"""
    
    # Chargement des données
    df_genre_trimestre, df_repartition_genre, df_genre_commune = charger_donnees_genre()
    
    if df_genre_trimestre is None or df_repartition_genre is None or df_genre_commune is None:
        st.error("🚨 Impossible de charger les données de genre")
        st.info("Veuillez vous assurer que les fichiers Excel sont présents dans le dossier 'genre/'")
        return
    
    # Titre principal avec style
    st.markdown("""
    <h2 style="color: #f39c12; text-align: center; margin-bottom: 2rem;">
        👫 Analyse de la Répartition par Genre
    </h2>
    """, unsafe_allow_html=True)
    
    # Sélection de la vue
    vue_selectionnee = st.selectbox(
        "📋 Sélectionner une vue",
        ["Vue d'ensemble", "Analyse par commune", "Analyse par type de parcelle", "Évolution temporelle"],
        key="vue_genre"
    )
    
    # Objectif personnalisable
    col1, col2 = st.columns([2, 1])
    with col2:
        objectif_femmes = st.slider(
            "🎯 Objectif % femmes",
            min_value=10,
            max_value=50,
            value=30,
            step=1,
            key="objectif_genre"
        )
    
    # Vérification des colonnes nécessaires
    if "Total_Nombre" not in df_repartition_genre.columns:
        st.error("La colonne 'Total_Nombre' n'existe pas dans les données de répartition")
        st.info("Colonnes disponibles: " + str(list(df_repartition_genre.columns)))
        return
    
    # Calcul des statistiques globales
    try:
        total_femmes = int(df_repartition_genre[df_repartition_genre["Genre"] == "Femme"]["Total_Nombre"].iloc[0])
        total_hommes = int(df_repartition_genre[df_repartition_genre["Genre"] == "Homme"]["Total_Nombre"].iloc[0])
        total_general = total_femmes + total_hommes
        pourcentage_femmes = round((total_femmes / total_general) * 100, 1)
        ratio_hf = round(total_hommes / total_femmes, 2)
    except (IndexError, KeyError) as e:
        st.error(f"Erreur lors du calcul des statistiques: {e}")
        st.info("Vérifiez que les données contiennent bien les genres 'Femme' et 'Homme'")
        return
    
    # Métriques principales (toujours visibles)
    st.markdown('<div class="section-header">📈 STATISTIQUES GLOBALES</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_modern_metric_card("👥 TOTAL PERSONNES", total_general, "metric-card-total"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_modern_metric_card("👨 HOMMES", total_hommes, "metric-card-male"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_modern_metric_card("👩 FEMMES", total_femmes, "metric-card-female"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_modern_metric_card("⚖️ RATIO H/F", ratio_hf, "ratio-card"), unsafe_allow_html=True)
    
    # Contenu selon la vue sélectionnée
    if vue_selectionnee == "Vue d'ensemble":
        st.markdown('<div class="section-header">🎯 OBJECTIF PARITÉ</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fig_gauge = create_gauge_chart(pourcentage_femmes, "Pourcentage de femmes", objectif_femmes)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            colors = ['#3498db', '#e91e63']
            fig_pie = create_modern_pie_chart(
                df_repartition_genre,
                names="Genre",
                values="Total_Nombre",
                title="Répartition Globale Hommes/Femmes",
                colors=colors
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    elif vue_selectionnee == "Analyse par commune":
        st.markdown('<div class="section-header">🗺️ ANALYSE PAR COMMUNE</div>', unsafe_allow_html=True)
        
        # Vérification des colonnes nécessaires
        if "communeSenegal" not in df_genre_commune.columns:
            st.error("La colonne 'communeSenegal' n'existe pas dans les données par commune")
            st.info("Colonnes disponibles: " + str(list(df_genre_commune.columns)))
            return
        
        # Filtre commune
        communes = df_genre_commune["communeSenegal"].unique()
        commune_selectionnee = st.selectbox("🏘️ Sélectionner une commune", communes)
        
        # Données de la commune sélectionnée
        df_commune = df_genre_commune[df_genre_commune["communeSenegal"] == commune_selectionnee]
        
        if df_commune.empty:
            st.error(f"Aucune donnée trouvée pour la commune: {commune_selectionnee}")
            return
        
        try:
            femmes_c = int(df_commune["Femme"].iloc[0])
            hommes_c = int(df_commune["Homme"].iloc[0])
            total_c = femmes_c + hommes_c
            pourcentage_femmes_c = round((femmes_c / total_c) * 100, 1)
        except (KeyError, IndexError) as e:
            st.error(f"Erreur lors du calcul des statistiques pour la commune: {e}")
            st.info("Vérifiez que les colonnes 'Femme' et 'Homme' existent dans les données")
            return
        
        # Métriques de la commune
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Total", f"{total_c:,}")
        with col2:
            st.metric("👨 Hommes", f"{hommes_c:,}")
        with col3:
            st.metric("👩 Femmes", f"{femmes_c:,}")
        
        # Graphiques de la commune
        col1, col2 = st.columns(2)
        
        with col1:
            fig_gauge_commune = create_gauge_chart(pourcentage_femmes_c, f"% Femmes - {commune_selectionnee}", objectif_femmes)
            st.plotly_chart(fig_gauge_commune, use_container_width=True)
        
        with col2:
            df_temp = pd.DataFrame({
                "Genre": ["Homme", "Femme"],
                "Nombre": [hommes_c, femmes_c]
            })
            fig_pie_commune = create_modern_pie_chart(
                df_temp,
                names="Genre",
                values="Nombre",
                title=f"Répartition - {commune_selectionnee}",
                colors=['#3498db', '#e91e63']
            )
            st.plotly_chart(fig_pie_commune, use_container_width=True)
        
        # Vue globale par commune
        st.markdown("### 🌍 Vue d'ensemble - Toutes les communes")
        df_long = df_genre_commune.melt(
            id_vars=["communeSenegal"],
            value_vars=["Femme", "Homme"],
            var_name="Genre",
            value_name="Nombre"
        )
        
        fig_communes = create_stacked_bar_chart(
            df_long,
            x="communeSenegal",
            y="Nombre",
            color="Genre",
            title="Répartition du genre par commune",
            color_map={"Homme": "#3498db", "Femme": "#e91e63"}
        )
        st.plotly_chart(fig_communes, use_container_width=True)
    
    elif vue_selectionnee == "Analyse par type de parcelle":
        st.markdown('<div class="section-header">📦 ANALYSE PAR TYPE DE PARCELLE</div>', unsafe_allow_html=True)
        
        types_parcelles = ["Individuel", "Collectif", "Mandataires"]
        type_selectionne = st.selectbox("📋 Sélectionner un type de parcelle", types_parcelles)
        
        col_nb = f"{type_selectionne}_Nombre"
        
        if col_nb in df_repartition_genre.columns:
            fig_type = create_modern_bar_chart(
                df_repartition_genre,
                x="Genre",
                y=col_nb,
                color="Genre",
                title=f"Répartition par genre - {type_selectionne}",
                color_map={"Homme": "#3498db", "Femme": "#e91e63"}
            )
            st.plotly_chart(fig_type, use_container_width=True)
            
            # Affichage des statistiques pour ce type
            col1, col2 = st.columns(2)
            with col1:
                hommes_type = int(df_repartition_genre[df_repartition_genre["Genre"] == "Homme"][col_nb].iloc[0])
                st.metric("👨 Hommes", f"{hommes_type:,}")
            with col2:
                femmes_type = int(df_repartition_genre[df_repartition_genre["Genre"] == "Femme"][col_nb].iloc[0])
                st.metric("👩 Femmes", f"{femmes_type:,}")
        else:
            st.error(f"La colonne '{col_nb}' n'existe pas dans les données")
            st.info("Colonnes disponibles: " + str(list(df_repartition_genre.columns)))
        
        # Comparaison de tous les types
        st.markdown("### 📊 Comparaison tous types")
        comparison_data = []
        for type_p in types_parcelles:
            col_nb = f"{type_p}_Nombre"
            if col_nb in df_repartition_genre.columns:
                for _, row in df_repartition_genre.iterrows():
                    comparison_data.append({
                        "Type": type_p,
                        "Genre": row["Genre"],
                        "Nombre": row[col_nb]
                    })
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            fig_comparison = create_stacked_bar_chart(
                df_comparison,
                x="Type",
                y="Nombre",
                color="Genre",
                title="Comparaison par type de parcelle",
                color_map={"Homme": "#3498db", "Femme": "#e91e63"}
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
    
    elif vue_selectionnee == "Évolution temporelle":
        st.markdown('<div class="section-header">📅 ÉVOLUTION TEMPORELLE</div>', unsafe_allow_html=True)
        
        if "PeriodeTrimestrielle" in df_genre_trimestre.columns:
            # Vérification des colonnes nécessaires
            if "Femme" not in df_genre_trimestre.columns or "Homme" not in df_genre_trimestre.columns:
                st.error("Les colonnes 'Femme' et 'Homme' n'existent pas dans les données trimestrielles")
                st.info("Colonnes disponibles: " + str(list(df_genre_trimestre.columns)))
                return
            
            # Graphique d'évolution
            fig_evol = create_area_chart(
                df_genre_trimestre,
                x="PeriodeTrimestrielle",
                y_cols=["Femme", "Homme"],
                title="Évolution trimestrielle par genre",
                color_map={"Homme": "#3498db", "Femme": "#e91e63"}
            )
            st.plotly_chart(fig_evol, use_container_width=True)
            
            # Tableau de données
            st.markdown("### 📋 Données détaillées")
            st.dataframe(df_genre_trimestre, use_container_width=True)
        else:
            st.error("La colonne 'PeriodeTrimestrielle' n'existe pas dans les données")
            st.info("Colonnes disponibles: " + str(list(df_genre_trimestre.columns)))

# Fonction principale pour exécution standalone (optionnelle)
def main():
    """Fonction principale pour exécution standalone"""
    st.set_page_config(
        page_title="Analyse Genre - Dashboard",
        page_icon="👫",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 ANALYSE FONCIÈRE GENRE")
    afficher_repartition_genre()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; margin-top: 2rem;">
        <p>📊 Dashboard Analyse Foncière Genre | PROCASEF Boundou</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
