import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def afficher_analyse_parcelles():
    """Module d'analyse des parcelles et levées pour le tableau de bord PROCASEF"""
    
    st.header("📊 Analyse des Parcelles et Levées")
    
    # Fonction chargement des données déjà définies dans dashboard.py, donc on les utilise directement
    df_levee = charger_levee_par_commune()
    df_parcelles = charger_parcelles_terrain_periode()
    
    # Chargement spécifique pour ce module
    @st.cache_data
    def charger_parcelles_post_traitement():
        """Charge les données des parcelles post-traitées par géométrie"""
        try:
            df = pd.read_excel("data/Parcelles post traites par geom.xlsx", engine="openpyxl")
            df.columns = df.columns.str.strip().str.lower()
            return df
        except Exception as e:
            st.error(f"Erreur fichier parcelles post-traitées : {e}")
            return pd.DataFrame()
    
    df_post_traitement = charger_parcelles_post_traitement()
    
    # Création de 3 onglets pour l'analyse
    tab1, tab2, tab3 = st.tabs(["🏘️ Levées par Commune/Région", "📆 Évolution Temporelle", "📊 Post-traitement Géométrique"])
    
    # Onglet 1: Analyse des levées par commune et région
    with tab1:
        st.subheader("🏘️ Analyse des Levées par Commune et Région")
        
        if not df_levee.empty:
            # Vérification des colonnes
            expected_cols = ['region', 'commune', 'parcelles terrain', 'parcelles delimitées et enquetées (fourni par l\'opérateur)(urm)']
            missing_cols = [col for col in expected_cols if col not in df_levee.columns]
            
            if missing_cols:
                st.warning(f"Attention: Les colonnes suivantes sont manquantes dans le fichier: {', '.join(missing_cols)}")
                st.write("Colonnes disponibles:", df_levee.columns.tolist())
            else:
                # Filtrage par région
                regions = df_levee['region'].unique()
                region_sel = st.selectbox("Filtrer par région", ["Toutes"] + list(regions), key='region_filter')
                
                df_filtre = df_levee if region_sel == "Toutes" else df_levee[df_levee['region'] == region_sel]
                
                # Graphique par commune
                st.subheader("📊 Comparaison des Parcelles par Commune")
                
                # Création d'un graphique à barres groupées
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_filtre['commune'],
                    y=df_filtre['parcelles terrain'],
                    name='Parcelles Terrain',
                    marker_color='royalblue'
                ))
                fig.add_trace(go.Bar(
                    x=df_filtre['commune'],
                    y=df_filtre['parcelles delimitées et enquetées (fourni par l\'opérateur)(urm)'],
                    name='Parcelles URM',
                    marker_color='firebrick'
                ))

                fig.update_layout(
                    title='Comparaison des Parcelles Terrain vs URM par Commune',
                    xaxis_tickangle=-45,
                    xaxis_title='Commune',
                    yaxis_title='Nombre de Parcelles',
                    barmode='group',
                    height=600
                )

                st.plotly_chart(fig, use_container_width=True)
                
                # Si "Toutes" les régions sont sélectionnées, afficher aussi le graphique par région
                if region_sel == "Toutes":
                    st.subheader("🌍 Comparaison des Parcelles par Région")
                    
                    # Agrégation par région
                    df_region = df_levee.groupby('region')[
                        ['parcelles terrain', 'parcelles delimitées et enquetées (fourni par l\'opérateur)(urm)']
                    ].sum().reset_index()
                    
                    # Création du graphique par région
                    fig_region = go.Figure()
                    fig_region.add_trace(go.Bar(
                        x=df_region['region'],
                        y=df_region['parcelles terrain'],
                        name='Parcelles Terrain',
                        marker_color='royalblue'
                    ))
                    fig_region.add_trace(go.Bar(
                        x=df_region['region'],
                        y=df_region['parcelles delimitées et enquetées (fourni par l\'opérateur)(urm)'],
                        name='Parcelles URM',
                        marker_color='firebrick'
                    ))

                    fig_region.update_layout(
                        title='Comparaison des Parcelles Terrain vs URM par Région',
                        xaxis_tickangle=-45,
                        xaxis_title='Région',
                        yaxis_title='Nombre de Parcelles',
                        barmode='group',
                        height=500
                    )

                    st.plotly_chart(fig_region, use_container_width=True)
                
                # Afficher la table de données
                with st.expander("📋 Voir les données"):
                    st.dataframe(df_filtre)
        else:
            st.error("Aucune donnée disponible pour l'analyse des levées par commune.")

    # Onglet 2: Évolution temporelle
    with tab2:
        st.subheader("📆 Évolution Temporelle des Levées")
        
        if not df_parcelles.empty:
            # Vérification des colonnes
            expected_cols = ['date de debut', 'date de fin', 'commune', 'levee', 'lots']
            missing_cols = [col for col in expected_cols if col not in df_parcelles.columns]
            
            if missing_cols:
                st.warning(f"Attention: Les colonnes suivantes sont manquantes dans le fichier: {', '.join(missing_cols)}")
                st.write("Colonnes disponibles:", df_parcelles.columns.tolist())
            else:
                # Filtres
                col1, col2 = st.columns(2)
                
                with col1:
                    commune_options = df_parcelles['commune'].dropna().unique()
                    commune_sel = st.selectbox("Filtrer par commune", ["Toutes"] + sorted(commune_options))
                
                with col2:
                    if 'lots' in df_parcelles.columns:
                        lot_options = df_parcelles['lots'].dropna().unique()
                        lot_sel = st.selectbox("Filtrer par lot", ["Tous"] + sorted(lot_options))
                    else:
                        lot_sel = "Tous"
                
                # Filtres temporels
                date_min = df_parcelles['date de debut'].min()
                date_max = df_parcelles['date de fin'].max()
                
                if pd.isna(date_min) or pd.isna(date_max):
                    st.warning("Dates invalides ou manquantes dans les données.")
                else:
                    date_min = pd.to_datetime(date_min).to_pydatetime()
                    date_max = pd.to_datetime(date_max).to_pydatetime()
                    
                    date_range = st.slider(
                        "Période d'analyse",
                        min_value=date_min,
                        max_value=date_max,
                        value=(date_min, date_max),
                        format="YYYY-MM-DD"
                    )
                    
                    # Application des filtres
                    df_filtre = df_parcelles[
                        (df_parcelles['date de debut'] >= date_range[0]) &
                        (df_parcelles['date de fin'] <= date_range[1])
                    ]
                    
                    if commune_sel != "Toutes":
                        df_filtre = df_filtre[df_filtre['commune'] == commune_sel]
                    
                    if lot_sel != "Tous" and 'lots' in df_filtre.columns:
                        df_filtre = df_filtre[df_filtre['lots'] == lot_sel]
                    
                    if df_filtre.empty:
                        st.warning("Aucune donnée disponible pour cette sélection.")
                    else:
                        # Création d'une colonne pour les périodes (mois/année)
                        df_filtre['periode'] = df_filtre['date de debut'].dt.to_period('M').astype(str)
                        
                        # Graphique d'évolution temporelle
                        st.subheader("📈 Évolution des Levées dans le Temps")
                        
                        evolution = df_filtre.groupby('periode').size().reset_index(name='nombre')
                        
                        fig = px.line(
                            evolution, 
                            x='periode', 
                            y='nombre',
                            markers=True,
                            title="Évolution du nombre de levées par période"
                        )
                        
                        fig.update_layout(
                            xaxis_title="Période",
                            yaxis_title="Nombre de levées",
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Si la colonne "levee" existe, afficher l'évolution par type de levée
                        if 'levee' in df_filtre.columns:
                            st.subheader("📊 Évolution par Type de Levée")
                            
                            levee_evolution = df_filtre.groupby(['periode', 'levee']).size().reset_index(name='nombre')
                            
                            fig_levee = px.line(
                                levee_evolution,
                                x='periode',
                                y='nombre',
                                color='levee',
                                markers=True,
                                title="Évolution du nombre de levées par type"
                            )
                            
                            fig_levee.update_layout(
                                xaxis_title="Période",
                                yaxis_title="Nombre de levées",
                                height=500
                            )
                            
                            st.plotly_chart(fig_levee, use_container_width=True)
                        
                        # Afficher la table de données
                        with st.expander("📋 Voir les données"):
                            st.dataframe(df_filtre)
        else:
            st.error("Aucune donnée disponible pour l'analyse de l'évolution temporelle.")

    # Onglet 3: Post-traitement géométrique
    with tab3:
        st.subheader("📊 Analyse du Post-traitement Géométrique")
        
        if not df_post_traitement.empty:
            # Vérification des colonnes
            expected_cols = ['geom', 'commune', 'total parcelle reçue', 'parcelle post traité (prête à être valider', 
                            'nombre de parcelle dont la jointure est correcte', 'nombre de parcelle dont la jointure n\'a pas fonctionné',
                            'nombre de parcelle individuelle', 'nombre de parcelle collective', 'lot']
            
            # Normalisation des noms de colonnes pour la vérification
            normalized_cols = [col.lower().strip() for col in df_post_traitement.columns]
            df_post_traitement.columns = normalized_cols
            
            # Adaptez les noms de colonnes normalisés pour correspondre à votre dataframe
            missing_cols = []
            for col in expected_cols:
                if not any(expected_col.lower().strip() in norm_col for norm_col in normalized_cols):
                    missing_cols.append(col)
            
            if missing_cols:
                st.warning(f"Attention: Les colonnes suivantes sont manquantes dans le fichier: {', '.join(missing_cols)}")
                st.write("Colonnes disponibles:", df_post_traitement.columns.tolist())
            
            # Filtres
            col1, col2 = st.columns(2)
            
            with col1:
                if 'geom' in df_post_traitement.columns:
                    geom_options = df_post_traitement['geom'].dropna().unique()
                    geom_sel = st.selectbox("Filtrer par géométrie", ["Toutes"] + sorted(geom_options))
                else:
                    geom_sel = "Toutes"
            
            with col2:
                if 'commune' in df_post_traitement.columns:
                    commune_options = df_post_traitement['commune'].dropna().unique()
                    commune_sel = st.selectbox("Filtrer par commune", ["Toutes"] + sorted(commune_options), key='commune_tab3')
                else:
                    commune_sel = "Toutes"
            
            # Application des filtres
            df_filtre = df_post_traitement.copy()
            
            if geom_sel != "Toutes" and 'geom' in df_filtre.columns:
                df_filtre = df_filtre[df_filtre['geom'] == geom_sel]
            
            if commune_sel != "Toutes" and 'commune' in df_filtre.columns:
                df_filtre = df_filtre[df_filtre['commune'] == commune_sel]
            
            if df_filtre.empty:
                st.warning("Aucune donnée disponible pour cette sélection.")
            else:
                # Création des graphiques
                st.subheader("📊 Statistiques de Post-traitement")
                
                # Identifier les colonnes numériques pertinentes
                num_cols = [
                    col for col in df_filtre.columns 
                    if ('parcelle' in col or 'total' in col or 'nombre' in col) and 
                    df_filtre[col].dtype in ['int64', 'float64']
                ]
                
                if num_cols:
                    # Créer un dataframe agrégé pour l'affichage
                    if geom_sel == "Toutes" and 'geom' in df_filtre.columns:
                        # Agrégation par géométrie
                        df_agg = df_filtre.groupby('geom')[num_cols].sum().reset_index()
                        category_col = 'geom'
                    elif commune_sel == "Toutes" and 'commune' in df_filtre.columns:
                        # Agrégation par commune
                        df_agg = df_filtre.groupby('commune')[num_cols].sum().reset_index()
                        category_col = 'commune'
                    else:
                        # Pas d'agrégation nécessaire
                        df_agg = df_filtre
                        category_col = 'index'
                        df_agg[category_col] = "Sélection actuelle"
                    
                    # Graphique de comparaison
                    fig = go.Figure()
                    
                    for col in num_cols:
                        fig.add_trace(go.Bar(
                            x=df_agg[category_col],
                            y=df_agg[col],
                            name=col.capitalize(),
                        ))
                    
                    fig.update_layout(
                        title=f"Comparaison des parcelles par {category_col}",
                        xaxis_tickangle=-45,
                        xaxis_title=category_col.capitalize(),
                        yaxis_title="Nombre de parcelles",
                        barmode='group',
                        height=600
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Graphique circulaire de la répartition
                    st.subheader("🍩 Répartition des Types de Parcelles")
                    
                    # Sélectionner les colonnes de répartition (par exemple, individuelle vs collective)
                    pie_cols = [col for col in num_cols if 'individuelle' in col or 'collective' in col]
                    
                    if pie_cols:
                        pie_data = pd.DataFrame({
                            'Type': [col.replace('nombre de parcelle ', '').capitalize() for col in pie_cols],
                            'Valeur': [df_filtre[col].sum() for col in pie_cols]
                        })
                        
                        fig_pie = px.pie(
                            pie_data,
                            values='Valeur',
                            names='Type',
                            title="Répartition par type de parcelle"
                        )
                        
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Graphique de comparaison entre parcelles reçues et post-traitées
                    st.subheader("📈 Parcelles Reçues vs Post-traitées")
                    
                    comparison_cols = [
                        col for col in num_cols 
                        if 'total parcelle reçue' in col or 'parcelle post traité' in col
                    ]
                    
                    if len(comparison_cols) >= 2:
                        if 'lot' in df_filtre.columns:
                            # Par lot
                            df_lot = df_filtre.groupby('lot')[comparison_cols].sum().reset_index()
                            
                            fig_comp = go.Figure()
                            
                            for col in comparison_cols:
                                fig_comp.add_trace(go.Bar(
                                    x=df_lot['lot'],
                                    y=df_lot[col],
                                    name=col.capitalize()
                                ))
                            
                            fig_comp.update_layout(
                                title="Comparaison par lot",
                                xaxis_title="Lot",
                                yaxis_title="Nombre de parcelles",
                                barmode='group',
                                height=500
                            )
                            
                            st.plotly_chart(fig_comp, use_container_width=True)
                        
                        # Efficacité du traitement
                        if 'total parcelle reçue' in df_filtre.columns and 'parcelle post traité (prête à être valider' in df_filtre.columns:
                            st.subheader("⚙️ Efficacité du Post-traitement")
                            
                            # Calculer le taux de traitement
                            df_filtre['taux_traitement'] = (df_filtre['parcelle post traité (prête à être valider'] / 
                                                        df_filtre['total parcelle reçue'] * 100)
                            
                            # Agrégation par commune ou géométrie
                            if 'commune' in df_filtre.columns:
                                agg_col = 'commune'
                            elif 'geom' in df_filtre.columns:
                                agg_col = 'geom'
                            else:
                                agg_col = None
                            
                            if agg_col:
                                df_eff = df_filtre.groupby(agg_col).agg({
                                    'total parcelle reçue': 'sum',
                                    'parcelle post traité (prête à être valider': 'sum'
                                }).reset_index()
                                
                                df_eff['taux_traitement'] = (df_eff['parcelle post traité (prête à être valider'] / 
                                                            df_eff['total parcelle reçue'] * 100)
                                
                                fig_eff = px.bar(
                                    df_eff,
                                    x=agg_col,
                                    y='taux_traitement',
                                    text_auto='.1f',
                                    title=f"Taux de traitement par {agg_col} (%)"
                                )
                                
                                fig_eff.update_traces(texttemplate='%{text}%', textposition='outside')
                                fig_eff.update_layout(
                                    xaxis_title=agg_col.capitalize(),
                                    yaxis_title="Taux de traitement (%)",
                                    height=500
                                )
                                
                                st.plotly_chart(fig_eff, use_container_width=True)
                
                # Afficher la table de données
                with st.expander("📋 Voir les données"):
                    st.dataframe(df_filtre)
                    
                    # Option de téléchargement
                    csv = df_filtre.to_csv(index=False)
                    st.download_button(
                        label="Télécharger les données filtrées (CSV)",
                        data=csv,
                        file_name="parcelles_post_traitees_filtrees.csv",
                        mime="text/csv",
                    )
        else:
            st.error("Aucune donnée disponible pour l'analyse du post-traitement géométrique.")
