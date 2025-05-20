import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

def charger_levee_par_commune():
    """Charge et prépare les données de levée par commune"""
    try:
        df = pd.read_excel("data/Levee par commune Terrain_URM.xlsx", engine="openpyxl")
        # Normalisation des noms de colonnes
        df.columns = df.columns.str.strip().str.lower()
        
        # Conversion des types de données (à ajuster selon le contenu réel)
        if 'superficie' in df.columns:
            df['superficie'] = pd.to_numeric(df['superficie'], errors='coerce')
        if 'nombre_parcelles' in df.columns:
            df['nombre_parcelles'] = pd.to_numeric(df['nombre_parcelles'], errors='coerce')
        
        # Remplacer les valeurs manquantes
        df = df.fillna({'commune': 'Non spécifié'})
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier de levée par commune: {e}")
        return pd.DataFrame()

def charger_parcelles_terrain_periode():
    """Charge et prépare les données des parcelles par période"""
    try:
        df = pd.read_excel("data/Parcelles_terrain_periode.xlsx", engine="openpyxl")
        # Normalisation des noms de colonnes
        df.columns = df.columns.str.strip().str.lower()
        
        # Si des colonnes de dates sont présentes, les convertir au format datetime
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Conversion des types de données numériques
        numeric_columns = ['superficie', 'nombre', 'quantite']
        for col in df.columns:
            if any(num_col in col.lower() for num_col in numeric_columns):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier des parcelles par période: {e}")
        return pd.DataFrame()

def afficher_post_traitement(df_post=None):
    """Affichage du dashboard de post-traitement"""
    # Titre de la section
    st.header("📊 Post-traitement des données parcellaires")
    
    # Charger les données si elles ne sont pas déjà chargées
    df_levee = charger_levee_par_commune()
    df_parcelles_periode = charger_parcelles_terrain_periode()
    
    # Vérifier si les données sont disponibles
    if df_levee.empty and df_parcelles_periode.empty:
        st.warning("Aucune donnée de post-traitement n'est disponible.")
        return
    
    # Création des onglets pour organiser l'information
    tab1, tab2, tab3 = st.tabs(["Statistiques générales", "Analyse par commune", "Évolution temporelle"])
    
    with tab1:
        afficher_statistiques_generales(df_levee, df_parcelles_periode)
    
    with tab2:
        afficher_analyse_par_commune(df_levee)
    
    with tab3:
        afficher_evolution_temporelle(df_parcelles_periode)

def afficher_statistiques_generales(df_levee, df_parcelles_periode):
    """Affiche les statistiques générales"""
    st.subheader("Vue d'ensemble des données")
    
    # Créer des colonnes pour les métriques
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcul des métriques principales
    total_communes = len(df_levee['commune'].unique()) if 'commune' in df_levee.columns else 0
    total_parcelles = df_levee['nombre_parcelles'].sum() if 'nombre_parcelles' in df_levee.columns else 0
    total_superficie = df_levee['superficie'].sum() if 'superficie' in df_levee.columns else 0
    
    # Calculer le nombre de périodes si disponible
    nb_periodes = 0
    if not df_parcelles_periode.empty:
        date_columns = [col for col in df_parcelles_periode.columns if 'date' in col.lower() or 'periode' in col.lower()]
        if date_columns:
            periodes = df_parcelles_periode[date_columns[0]].unique()
            nb_periodes = len([p for p in periodes if p == p])  # Enlever les NaN
    
    # Affichage des métriques
    with col1:
        st.metric("Communes", f"{total_communes}")
    with col2:
        st.metric("Parcelles", f"{int(total_parcelles)}")
    with col3:
        st.metric("Superficie totale", f"{total_superficie:.2f} ha")
    with col4:
        st.metric("Périodes d'analyse", f"{nb_periodes}")
    
    # Séparateur
    st.markdown("---")
    
    # Graphique de répartition des parcelles par statut si disponible
    if 'statut' in df_parcelles_periode.columns:
        st.subheader("Répartition des parcelles par statut")
        repartition_statut = df_parcelles_periode['statut'].value_counts().reset_index()
        repartition_statut.columns = ['Statut', 'Nombre']
        
        fig = px.pie(repartition_statut, values='Nombre', names='Statut', 
                    title='Répartition des parcelles par statut',
                    color_discrete_sequence=px.colors.qualitative.G10)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des statistiques principales
    st.subheader("Aperçu des données")
    
    # Afficher un aperçu du DataFrame des levées
    if not df_levee.empty:
        st.write("**Données de levée par commune**")
        st.dataframe(df_levee.head())
    
    # Afficher un aperçu du DataFrame des parcelles par période
    if not df_parcelles_periode.empty:
        st.write("**Données des parcelles par période**")
        st.dataframe(df_parcelles_periode.head())

def afficher_analyse_par_commune(df_levee):
    """Affiche l'analyse des données par commune"""
    if df_levee.empty:
        st.info("Aucune donnée disponible pour l'analyse par commune.")
        return
    
    st.subheader("Analyse par commune")
    
    # Filtrer les données par commune si nécessaire
    communes = df_levee['commune'].unique().tolist() if 'commune' in df_levee.columns else []
    if communes:
        commune_selectionnee = st.selectbox("Sélectionner une commune", options=["Toutes"] + communes)
        
        df_filtre = df_levee
        if commune_selectionnee != "Toutes":
            df_filtre = df_levee[df_levee['commune'] == commune_selectionnee]
        
        # Graphique de répartition des parcelles par commune
        if 'nombre_parcelles' in df_filtre.columns and commune_selectionnee == "Toutes":
            st.subheader("Nombre de parcelles par commune")
            
            fig = px.bar(df_filtre.sort_values('nombre_parcelles', ascending=False), 
                         x='commune', y='nombre_parcelles',
                         labels={'commune': 'Commune', 'nombre_parcelles': 'Nombre de parcelles'},
                         color='nombre_parcelles',
                         color_continuous_scale='Viridis')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Graphique de superficie par commune
        if 'superficie' in df_filtre.columns and commune_selectionnee == "Toutes":
            st.subheader("Superficie par commune")
            
            fig = px.bar(df_filtre.sort_values('superficie', ascending=False), 
                         x='commune', y='superficie',
                         labels={'commune': 'Commune', 'superficie': 'Superficie (ha)'},
                         color='superficie',
                         color_continuous_scale='Viridis')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques détaillées pour une commune spécifique
        if commune_selectionnee != "Toutes":
            st.subheader(f"Statistiques détaillées pour {commune_selectionnee}")
            
            # Calculer des statistiques plus détaillées pour cette commune
            stats_commune = df_filtre.describe().T
            st.dataframe(stats_commune)
            
            # Afficher les données brutes pour cette commune
            st.subheader(f"Données brutes pour {commune_selectionnee}")
            st.dataframe(df_filtre)

def afficher_evolution_temporelle(df_parcelles_periode):
    """Affiche l'évolution temporelle des parcelles"""
    if df_parcelles_periode.empty:
        st.info("Aucune donnée disponible pour l'analyse temporelle.")
        return
    
    st.subheader("Évolution temporelle")
    
    # Identifier les colonnes de date/période
    date_columns = [col for col in df_parcelles_periode.columns if 'date' in col.lower() or 'periode' in col.lower()]
    
    if date_columns:
        col_date = date_columns[0]  # Prendre la première colonne de date trouvée
        
        # Créer une colonne de période standardisée si nécessaire
        if pd.api.types.is_datetime64_any_dtype(df_parcelles_periode[col_date]):
            df_temp = df_parcelles_periode.copy()
            df_temp['periode_std'] = df_temp[col_date].dt.strftime('%Y-%m')
        else:
            df_temp = df_parcelles_periode.copy()
            df_temp['periode_std'] = df_temp[col_date]
        
        # Graphique d'évolution temporelle
        evolution = df_temp.groupby('periode_std').size().reset_index(name='count')
        evolution = evolution.sort_values('periode_std')
        
        fig = px.line(evolution, x='periode_std', y='count',
                      markers=True,
                      labels={'periode_std': 'Période', 'count': 'Nombre de parcelles'},
                      title="Évolution du nombre de parcelles traitées")
        st.plotly_chart(fig, use_container_width=True)
        
        # Si des colonnes de statut sont disponibles, montrer l'évolution par statut
        if 'statut' in df_temp.columns:
            evolution_statut = df_temp.groupby(['periode_std', 'statut']).size().reset_index(name='count')
            evolution_statut = evolution_statut.sort_values('periode_std')
            
            fig = px.line(evolution_statut, x='periode_std', y='count',
                          color='statut',
                          markers=True,
                          labels={'periode_std': 'Période', 'count': 'Nombre de parcelles', 'statut': 'Statut'},
                          title="Évolution du nombre de parcelles par statut")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune colonne de date ou période n'a été identifiée dans les données.")
    
    # Tableau récapitulatif des données
    st.subheader("Récapitulatif des données par période")
    
    # Identifier les colonnes numériques potentielles
    numeric_cols = df_parcelles_periode.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols and date_columns:
        # Créer un tableau récapitulatif par période
        recap = df_parcelles_periode.groupby(date_columns[0])[numeric_cols].sum().reset_index()
        st.dataframe(recap)
