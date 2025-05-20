import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import altair as alt
from streamlit_lottie import st_lottie
import requests
import openpyxl
import io
from datetime import datetime
import calendar
import locale

# Configurer la locale pour les noms de mois en français
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR')
    except:
        pass

# Configuration de la page
st.set_page_config(
    page_title="Statistiques Parcelles URM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour charger des animations Lottie
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Fonctions utilitaires
def formatter_pourcentage(val):
    return f"{val:.1f}%"

def formatter_nombre(val):
    return f"{int(val):,}".replace(",", " ")

# Palette de couleurs personnalisée
COLORS = {
    'primary': '#1f77b4',    # Bleu
    'secondary': '#ff7f0e',  # Orange
    'success': '#2ca02c',    # Vert
    'danger': '#d62728',     # Rouge
    'warning': '#ffbb78',    # Orange clair
    'info': '#17becf',       # Bleu clair
    'background': '#f9f9f9', # Fond gris clair
    'text': '#333333',       # Texte gris foncé
    
    # Palette pour les communes
    'communes': [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
        '#bcbd22', '#17becf', '#aec7e8', '#ffbb78'
    ]
}

# Fonction principale pour afficher le dashboard de post-traitement
def afficher_post_traitement(uploaded_file=None):
    # En-tête avec animation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style='text-align: center; background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin-bottom: 20px;'>
                <h1 style='color: #1f77b4;'>📊 Statistiques des parcelles URM</h1>
                <p style='font-size: 1.2em;'>Analyse comparative des données terrain et URM</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Initialiser df_source comme dictionnaire
    df_source = {}
    
    # Vérifier le type de données d'entrée et charger les données appropriées
    if uploaded_file is not None:
        if hasattr(uploaded_file, 'read'):
            # C'est un objet file_uploader
            file_content = uploaded_file.read()
            df_source = pd.read_excel(io.BytesIO(file_content), sheet_name=None)
        elif isinstance(uploaded_file, dict):
            # C'est déjà un dictionnaire de DataFrames (format attendu)
            df_source = uploaded_file
        elif isinstance(uploaded_file, pd.DataFrame):
            # C'est un DataFrame unique, on le met dans un dictionnaire
            st.warning("Un DataFrame unique a été fourni. Assurez-vous qu'il contient toutes les données nécessaires.")
            # Supposer que c'est la feuille principale
            df_source = {"Parcelles_terrain_periode": uploaded_file}
        else:
            st.error(f"Type de données non pris en charge: {type(uploaded_file)}")
            return
    else:
        # Utiliser un jeu de données d'exemple si aucun fichier n'est fourni
        try:
            df_source = pd.read_excel("Urm_Terrain_comparaison.xlsx", sheet_name=None)
        except:
            st.error("Veuillez télécharger le fichier Excel 'Urm_Terrain_comparaison.xlsx'")
            
            # Afficher une animation et un message d'attente
            lottie_upload = load_lottie_url("https://lottie.host/6c527ec1-0b8b-480d-afc7-6e5cf95675fd/fMQMn1hGtV.json")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st_lottie(lottie_upload, height=300, key="upload_animation")
                st.info("Téléchargez le fichier Excel avec les données des parcelles pour visualiser les statistiques.")
            return
    
    # Traitement des données
    df_parcelles_periode = df_source.get('Parcelles_terrain_periode')
    df_terrain_commune = df_source.get('Terrain par commune')
    
    if df_terrain_commune is None or df_parcelles_periode is None:
        st.error("Le fichier Excel doit contenir les feuilles 'Parcelles_terrain_periode' et 'Terrain par commune'")
        return
    
    # Nettoyage et préparation des données de comparaison par commune
    df_communes = df_terrain_commune.copy()
    df_communes = df_communes.dropna(subset=['Communes'])
    df_communes = df_communes[~df_communes['Communes'].str.contains('Taux|Total', case=False, na=False)]
    
    # Renommer les colonnes pour plus de clarté
    df_communes.columns = [col.replace('(fourni par l\'operateur)(URM)', '').strip() 
                          if isinstance(col, str) else col 
                          for col in df_communes.columns]
    
    # Préparation des données pour les graphiques
    df_communes['Différence'] = df_communes['Total Parcelles delimitées et enquetées'] - df_communes['Total Parcelles Terrain']
    df_communes['Pourcentage'] = (df_communes['Total Parcelles delimitées et enquetées'] / df_communes['Total Parcelles Terrain'] * 100).round(1)
    
    # Calculer les totaux
    total_terrain = df_communes['Total Parcelles Terrain'].sum()
    total_urm = df_communes['Total Parcelles delimitées et enquetées'].sum()
    pourcentage_global = (total_urm / total_terrain * 100).round(1)
    
    # Préparation des données de parcelles par période
    df_periode = df_parcelles_periode.copy()
    
    # Convertir les dates si nécessaire
    for col in ['Date début', 'Date fin']:
        if col in df_periode.columns:
            df_periode[col] = pd.to_datetime(df_periode[col], errors='coerce')
    
    # Filtrer les lignes avec des communes valides
    df_periode = df_periode.dropna(subset=['Commune'])
    df_periode = df_periode[~df_periode['Commune'].str.contains('Total', case=False, na=False)]

    # Création du dashboard
    # Mise en page avec tabs pour organiser les différentes vues
    tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "📈 Évolution temporelle", "🗺️ Détails par commune"])
    
    with tab1:
        # Cards pour montrer les KPIs principaux
        st.markdown("### 🔑 Indicateurs clés")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total parcelles terrain",
                value=formatter_nombre(total_terrain),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total parcelles URM",
                value=formatter_nombre(total_urm),
                delta=f"{formatter_nombre(total_urm - total_terrain)} vs terrain"
            )
        
        with col3:
            st.metric(
                label="Taux de réalisation",
                value=f"{pourcentage_global:.1f}%",
                delta=f"{pourcentage_global-100:.1f}%" if pourcentage_global != 100 else "À l'objectif"
            )
        
        with col4:
            communes_count = len(df_communes)
            st.metric(
                label="Nombre de communes",
                value=communes_count,
                delta=None
            )
        
        # Graphique de comparaison Terrain vs URM par commune
        st.markdown("### 📊 Comparaison Terrain vs URM par commune")
        
        # Préparer les données pour le graphique
        df_graph = df_communes.sort_values(by='Total Parcelles Terrain', ascending=False)
        
        # Créer un graphique à barres groupées avec Plotly
        fig = go.Figure()
        
        # Ajouter les barres pour les parcelles terrain
        fig.add_trace(go.Bar(
            x=df_graph['Communes'],
            y=df_graph['Total Parcelles Terrain'],
            name='Parcelles Terrain',
            marker_color=COLORS['primary'],
            text=df_graph['Total Parcelles Terrain'].apply(formatter_nombre),
            textposition='auto'
        ))
        
        # Ajouter les barres pour les parcelles URM
        fig.add_trace(go.Bar(
            x=df_graph['Communes'],
            y=df_graph['Total Parcelles delimitées et enquetées'],
            name='Parcelles URM',
            marker_color=COLORS['secondary'],
            text=df_graph['Total Parcelles delimitées et enquetées'].apply(formatter_nombre),
            textposition='auto'
        ))
        
        # Mise en forme du graphique
        fig.update_layout(
            barmode='group',
            title='Comparaison du nombre de parcelles par commune',
            xaxis_title='Commune',
            yaxis_title='Nombre de parcelles',
            legend_title='Type',
            template='plotly_white',
            height=500,
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique de pourcentage de réalisation par commune
        st.markdown("### 📈 Taux de réalisation par commune")
        
        # Créer un graphique à barres horizontales pour les pourcentages
        df_sorted = df_communes.sort_values(by='Pourcentage')
        
        fig_pct = go.Figure()
        
        # Définir les couleurs en fonction du taux de réalisation
        colors = df_sorted['Pourcentage'].apply(
            lambda x: COLORS['danger'] if x < 90 else 
                     (COLORS['warning'] if x < 100 else COLORS['success'])
        )
        
        # Ajouter les barres de pourcentage
        fig_pct.add_trace(go.Bar(
            y=df_sorted['Communes'],
            x=df_sorted['Pourcentage'],
            orientation='h',
            marker_color=colors,
            text=df_sorted['Pourcentage'].apply(formatter_pourcentage),
            textposition='auto'
        ))
        
        # Ajouter une ligne de référence à 100%
        fig_pct.add_shape(
            type="line",
            x0=100, y0=-0.5,
            x1=100, y1=len(df_sorted)-0.5,
            line=dict(color="black", width=2, dash="dot")
        )
        
        # Mise en forme du graphique
        fig_pct.update_layout(
            title='Taux de réalisation URM vs Terrain (%)',
            xaxis_title='Pourcentage de réalisation',
            yaxis_title='Commune',
            template='plotly_white',
            height=500,
            xaxis=dict(range=[0, max(df_sorted['Pourcentage'])*1.1])  # Ajuster l'échelle
        )
        
        st.plotly_chart(fig_pct, use_container_width=True)

    with tab2:
        st.markdown("### 📅 Évolution des levées de parcelles dans le temps")
        
        # Agréger les données par semaine et commune
        df_time = df_periode.copy()
        
        # S'assurer que les colonnes de date sont au format datetime
        if 'Date début' in df_time.columns:
            df_time['Semaine'] = df_time['Date début'].dt.strftime('%Y-%m-%d')
            df_time['Mois'] = df_time['Date début'].dt.strftime('%Y-%m')
            df_time['Mois_nom'] = df_time['Date début'].dt.strftime('%b %Y')
        
        # Définir les options d'affichage temporel
        time_options = ['Par semaine', 'Par mois', 'Cumulatif']
        time_display = st.radio("Affichage temporel:", time_options, horizontal=True)
        
        if time_display == 'Par semaine':
            # Grouper par semaine et commune
            df_weekly = df_time.groupby(['Semaine', 'Commune'])['Levée terrain'].sum().reset_index()
            df_weekly = df_weekly.sort_values(by='Semaine')
            
            # Créer un graphique d'évolution par semaine
            fig_weekly = px.line(
                df_weekly, 
                x='Semaine', 
                y='Levée terrain', 
                color='Commune',
                markers=True,
                title='Évolution hebdomadaire des levées de parcelles par commune',
                color_discrete_sequence=COLORS['communes']
            )
            
            fig_weekly.update_layout(
                xaxis_title='Semaine',
                yaxis_title='Nombre de parcelles levées',
                legend_title='Commune',
                hovermode="x unified",
                height=600
            )
            
            st.plotly_chart(fig_weekly, use_container_width=True)
            
        elif time_display == 'Par mois':
            # Grouper par mois et commune
            df_monthly = df_time.groupby(['Mois', 'Mois_nom', 'Commune'])['Levée terrain'].sum().reset_index()
            df_monthly = df_monthly.sort_values(by='Mois')
            
            # Créer un graphique d'évolution par mois
            fig_monthly = px.bar(
                df_monthly, 
                x='Mois_nom', 
                y='Levée terrain', 
                color='Commune',
                title='Évolution mensuelle des levées de parcelles par commune',
                color_discrete_sequence=COLORS['communes'],
                barmode='group'
            )
            
            fig_monthly.update_layout(
                xaxis_title='Mois',
                yaxis_title='Nombre de parcelles levées',
                legend_title='Commune',
                height=600,
                xaxis={'categoryorder':'array', 'categoryarray': sorted(df_monthly['Mois_nom'].unique())}
            )
            
            st.plotly_chart(fig_monthly, use_container_width=True)
            
        else:  # Cumulatif
            # Créer une version cumulative
            df_cum = df_time.sort_values(by='Date début')
            df_cum_grouped = df_cum.groupby(['Commune', 'Semaine'])['Levée terrain'].sum().reset_index()
            
            # Calculer le cumulatif par commune
            communes_list = df_cum_grouped['Commune'].unique()
            df_cumulative = pd.DataFrame()
            
            for commune in communes_list:
                df_temp = df_cum_grouped[df_cum_grouped['Commune'] == commune].copy()
                df_temp = df_temp.sort_values(by='Semaine')
                df_temp['Cumulatif'] = df_temp['Levée terrain'].cumsum()
                df_cumulative = pd.concat([df_cumulative, df_temp])
            
            # Créer un graphique cumulatif
            fig_cumul = px.line(
                df_cumulative, 
                x='Semaine', 
                y='Cumulatif', 
                color='Commune',
                markers=True,
                title='Évolution cumulative des levées de parcelles par commune',
                color_discrete_sequence=COLORS['communes']
            )
            
            # Ajouter les objectifs (basés sur les totaux du terrain)
            for commune in communes_list:
                target = df_communes[df_communes['Communes'] == commune.upper()]['Total Parcelles Terrain'].values
                if len(target) > 0:
                    fig_cumul.add_shape(
                        type="line",
                        x0=df_cumulative['Semaine'].min(),
                        y0=target[0],
                        x1=df_cumulative['Semaine'].max(),
                        y1=target[0],
                        line=dict(color=COLORS['danger'], width=1, dash="dash"),
                        name=f"Objectif {commune}"
                    )
            
            fig_cumul.update_layout(
                xaxis_title='Date',
                yaxis_title='Nombre cumulatif de parcelles',
                legend_title='Commune',
                hovermode="x unified",
                height=600
            )
            
            st.plotly_chart(fig_cumul, use_container_width=True)
        
        # Graphique de rythme journalier
        st.markdown("### ⏱️ Rythme journalier par commune")
        
        # Calculer le nombre de jours pour chaque période et le rythme
        df_rhythm = df_periode.copy()
        
        # Calculer le nombre de jours travaillés dans chaque période (date fin - date début + 1)
        df_rhythm['Jours'] = (df_rhythm['Date fin'] - df_rhythm['Date début']).dt.days + 1
        df_rhythm['Rythme journalier'] = df_rhythm['Levée terrain'] / df_rhythm['Jours']
        
        # Filtrer les lignes avec des valeurs valides
        df_rhythm = df_rhythm.dropna(subset=['Rythme journalier'])
        
        # Calculer le rythme moyen par commune
        df_rhythm_avg = df_rhythm.groupby('Commune')['Rythme journalier'].mean().reset_index()
        
        # Création du graphique de rythme journalier
        df_rhythm_avg = df_rhythm_avg.sort_values(by='Rythme journalier', ascending=False)
        
        fig_rhythm = px.bar(
            df_rhythm_avg,
            x='Commune',
            y='Rythme journalier',
            title='Rythme journalier moyen de levée de parcelles par commune',
            color='Rythme journalier',
            color_continuous_scale=px.colors.sequential.Blues
        )
        
        fig_rhythm.update_layout(
            xaxis_title='Commune',
            yaxis_title='Parcelles par jour (moyenne)',
            coloraxis_showscale=False,
            height=500
        )
        
        st.plotly_chart(fig_rhythm, use_container_width=True)
        
        # Tableau détaillé des périodes
        with st.expander("📋 Détails des périodes de travail"):
            st.markdown("### Périodes de travail par commune")
            
            # Formater le tableau pour l'affichage
            df_details = df_rhythm.copy()
            df_details['Date début'] = df_details['Date début'].dt.strftime('%d/%m/%Y')
            df_details['Date fin'] = df_details['Date fin'].dt.strftime('%d/%m/%Y')
            df_details['Rythme journalier'] = df_details['Rythme journalier'].round(1)
            
            # Sélectionner et réorganiser les colonnes pertinentes
            df_details = df_details[['Commune', 'Date début', 'Date fin', 'Jours', 'Levée terrain', 'Rythme journalier']]
            
            # Afficher le tableau avec mise en forme
            st.dataframe(
                df_details,
                column_config={
                    "Commune": "Commune",
                    "Date début": "Date de début",
                    "Date fin": "Date de fin",
                    "Jours": "Jours travaillés",
                    "Levée terrain": "Parcelles levées",
                    "Rythme journalier": st.column_config.NumberColumn(
                        "Rythme (parcelles/jour)",
                        format="%.1f",
                    )
                },
                hide_index=True,
                use_container_width=True
            )

    with tab3:
        st.markdown("### 🗺️ Détails par commune")
        
        # Sélecteur de commune
        commune_selectionnee = st.selectbox(
            "Sélectionner une commune",
            options=sorted(df_communes['Communes'].unique())
        )
        
        # Filtrer les données pour la commune sélectionnée
        commune_data = df_communes[df_communes['Communes'] == commune_selectionnee].iloc[0]
        
        # Afficher les KPIs de la commune
        st.markdown(f"#### Statistiques pour {commune_selectionnee}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Parcelles Terrain",
                value=formatter_nombre(commune_data['Total Parcelles Terrain']),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Parcelles URM",
                value=formatter_nombre(commune_data['Total Parcelles delimitées et enquetées']),
                delta=f"{formatter_nombre(commune_data['Différence'])}"
            )
        
        with col3:
            st.metric(
                label="Taux de réalisation",
                value=f"{commune_data['Pourcentage']:.1f}%",
                delta=f"{commune_data['Pourcentage'] - 100:.1f}%" if commune_data['Pourcentage'] != 100 else "À l'objectif"
            )
        
        with col4:
            # Récupérer le rythme moyen pour cette commune si disponible
            commune_rhythm = df_rhythm_avg[df_rhythm_avg['Commune'] == commune_selectionnee.title()]
            if not commune_rhythm.empty:
                rythme = commune_rhythm['Rythme journalier'].values[0]
                st.metric(
                    label="Rythme journalier",
                    value=f"{rythme:.1f} parcelles/jour",
                    delta=None
                )
            else:
                st.metric(
                    label="Rythme journalier",
                    value="N/A",
                    delta=None
                )
        
        # Graphique d'évolution temporelle pour la commune sélectionnée
        st.markdown("#### Évolution des levées de parcelles")
        
        # Filtrer les données temporelles pour la commune sélectionnée
        df_commune_time = df_periode[df_periode['Commune'] == commune_selectionnee.title()].copy()
        
        if not df_commune_time.empty:
            # Créer un graphique d'évolution cumulatif
            df_commune_time = df_commune_time.sort_values(by='Date début')
            df_commune_time['Cumul'] = df_commune_time['Levée terrain'].cumsum()
            
            # Créer un graphique combiné avec barres et ligne cumulative
            fig_commune = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Barres pour les levées par période
            fig_commune.add_trace(
                go.Bar(
                    x=df_commune_time['Date début'],
                    y=df_commune_time['Levée terrain'],
                    name="Levées par période",
                    marker_color=COLORS['primary']
                ),
                secondary_y=False
            )
            
            # Ligne pour le cumul
            fig_commune.add_trace(
                go.Scatter(
                    x=df_commune_time['Date début'],
                    y=df_commune_time['Cumul'],
                    name="Cumul",
                    line=dict(color=COLORS['secondary'], width=3),
                    mode='lines+markers'
                ),
                secondary_y=True
            )
            
            # Ajouter une ligne horizontale pour l'objectif
            target = commune_data['Total Parcelles Terrain']
            fig_commune.add_shape(
                type="line",
                x0=df_commune_time['Date début'].min(),
                y0=target,
                x1=df_commune_time['Date début'].max(),
                y1=target,
                line=dict(color=COLORS['danger'], width=2, dash="dash"),
                secondary_y=True
            )
            
            # Annotation pour l'objectif
            fig_commune.add_annotation(
                x=df_commune_time['Date début'].max(),
                y=target,
                text=f"Objectif: {formatter_nombre(target)}",
                showarrow=True,
                arrowhead=1,
                ax=50,
                ay=-30,
                secondary_y=True
            )
            
            # Mise en forme du graphique
            fig_commune.update_layout(
                title=f"Évolution des levées de parcelles à {commune_selectionnee}",
                xaxis_title="Date",
                legend_title="Mesure",
                hovermode="x unified",
                height=500
            )
            
            # Mise à jour des axes
            fig_commune.update_yaxes(
                title_text="Parcelles levées par période", 
                secondary_y=False
            )
            fig_commune.update_yaxes(
                title_text="Parcelles cumulées", 
                secondary_y=True
            )
            
            st.plotly_chart(fig_commune, use_container_width=True)
            
            # Tableau récapitulatif des périodes pour la commune
            st.markdown("#### Détails des périodes de travail")
            
            # Formater le tableau
            df_commune_details = df_commune_time.copy()
            df_commune_details['Date début'] = df_commune_details['Date début'].dt.strftime('%d/%m/%Y')
            df_commune_details['Date fin'] = df_commune_details['Date fin'].dt.strftime('%d/%m/%Y')
            
            # Calculer le rythme journalier
            df_commune_details['Jours'] = (pd.to_datetime(df_commune_details['Date fin']) - pd.to_datetime(df_commune_details['Date début'])).dt.days + 1
            df_commune_details['Rythme'] = df_commune_details['Levée terrain'] / df_commune_details['Jours']
            
            # Sélectionner et réorganiser les colonnes
            df_commune_details = df_commune_details[['Date début', 'Date fin', 'Jours', 'Levée terrain', 'Rythme', 'Cumul']]
            
            # Afficher le tableau
            st.dataframe(
                df_commune_details,
                column_config={
                    "Date début": "Date de début",
                    "Date fin": "Date de fin",
                    "Jours": "Jours travaillés",
                    "Levée terrain": "Parcelles levées",
                    "Rythme": st.column_config.NumberColumn(
                        "Rythme (parcelles/jour)",
                        format="%.1f"
                    ),
                    "Cumul": "Cumul des parcelles"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(f"Aucune donnée temporelle disponible pour {commune_selectionnee}")
    
    # Ajouter un pied de page avec des informations sur l'application
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #7f7f7f; padding: 10px;'>
            <p><small>Application développée pour l'analyse des données de parcelles URM</small></p>
            <p><small>© 2023 - Tableau de bord statistique</small></p>
        </div>
    """, unsafe_allow_html=True)

# Fonction principale de l'application
def main():
    # Sidebar avec logo et options
    st.sidebar.title("📊 Options d'analyse")
    
    # Upload de fichier
    uploaded_file = st.sidebar.file_uploader(
        "Télécharger le fichier Excel",
        type=["xlsx", "xls"],
        help="Téléchargez le fichier Excel contenant les données des parcelles"
    )
    
    # Afficher des informations sur l'application
    with st.sidebar.expander("ℹ️ À propos de l'application"):
        st.markdown("""
            Cette application analyse les données de parcelles URM et les compare aux données terrain.
            
            **Fonctionnalités:**
            * Comparaison des parcelles URM vs Terrain
            * Évolution temporelle des levées
            * Analyse détaillée par commune
            
            **Instructions:**
            1. Téléchargez le fichier Excel contenant les données
            2. Explorez les différents onglets d'analyse
            3. Filtrez les données selon vos besoins
        """)
    
    # Afficher les crédits et informations de version
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Version 1.0.0")
    st.sidebar.markdown("<small>Dernière mise à jour: Mai 2023</small>", unsafe_allow_html=True)
    
    # Afficher un bouton de téléchargement pour un modèle Excel
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Modèle de données")
    st.sidebar.markdown("""
        Téléchargez le modèle Excel pour préparer vos données:
    """)
    
    # Ce bouton serait normalement lié à un fichier de téléchargement
    # Dans une application réelle, vous utiliseriez st.sidebar.download_button
    # avec un fichier modèle préparé
    #st.sidebar.download_button(
    #    label="📥 Télécharger le modèle",
    #    data=get_binary_file_downloader_html("modele_urm_terrain.xlsx"),
    #    file_name="modele_urm_terrain.xlsx",
    #    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #)
    
    # Afficher le dashboard principal
    afficher_post_traitement(uploaded_file)

# Point d'entrée principal de l'application
if __name__ == "__main__":
    main()
