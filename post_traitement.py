import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import depuis le module data_loader pour éviter les imports circulaires
from data_loader import (
    charger_levee_par_commune,
    charger_parcelles_terrain_periode,
    charger_parcelles_post_traitement
)

def afficher_analyse_parcelles():
    """Module d'analyse des parcelles et levées pour le tableau de bord PROCASEF"""
    
    st.header("📊 Analyse des Parcelles et Levées")
    
    # Chargement des données
    df_levee = charger_levee_par_commune()
    df_parcelles = charger_parcelles_terrain_periode()
    df_post_traitement = charger_parcelles_post_traitement()
    
    # Création de 3 onglets pour l'analyse
    tab1, tab2, tab3 = st.tabs(["🏘️ Levées par Commune/Région", "📆 Évolution Temporelle", "📊 Post-traitement Géométrique"])
    
    # Onglet 1: Analyse des levées par commune et région
    with tab1:
        st.subheader("🏘️ Analyse des Levées par Commune et Région")
        
        if not df_levee.empty:
            # Normalisation des noms de colonnes
            df_levee.columns = df_levee.columns.str.lower().str.strip()
            
            # Mapping des colonnes possibles - mise à jour avec les vraies colonnes
            column_mapping = {
                'parcelles terrain': ['parcelles terrain', 'total parcelles terrain'],
                'parcelles urm': ['parcelles delimitées et enquetées (fourni par l\'opérateur)(urm)', 
                                 'total parcelles delimitées et enquetées (fourni par l\'operateur)(urm)',
                                 'parcelles delimitées et enquetées (fourni par l\'operateur)(urm)']
            }
            
            # Trouver les vraies colonnes dans le DataFrame
            actual_columns = {}
            for key, possible_names in column_mapping.items():
                for name in possible_names:
                    if name.lower().strip() in df_levee.columns:
                        actual_columns[key] = name.lower().strip()
                        break
            
            # Vérifier si on a les colonnes essentielles
            required_cols = ['region', 'commune']
            missing_required = [col for col in required_cols if col not in df_levee.columns]
            
            if missing_required:
                st.error(f"Colonnes essentielles manquantes: {', '.join(missing_required)}")
                st.write("Colonnes disponibles:", df_levee.columns.tolist())
            else:
                # Filtrage par région
                regions = df_levee['region'].unique()
                region_sel = st.selectbox("Filtrer par région", ["Toutes"] + list(regions), key='region_filter')
                
                df_filtre = df_levee if region_sel == "Toutes" else df_levee[df_levee['region'] == region_sel]
                
                # Graphique par commune si on a les colonnes de parcelles
                if actual_columns:
                    st.subheader("📊 Comparaison des Parcelles par Commune")
                    
                    # Création d'un graphique à barres groupées
                    fig = go.Figure()
                    
                    if 'parcelles terrain' in actual_columns:
                        fig.add_trace(go.Bar(
                            x=df_filtre['commune'],
                            y=df_filtre[actual_columns['parcelles terrain']],
                            name='Parcelles Terrain',
                            marker_color='royalblue'
                        ))
                    
                    if 'parcelles urm' in actual_columns:
                        fig.add_trace(go.Bar(
                            x=df_filtre['commune'],
                            y=df_filtre[actual_columns['parcelles urm']],
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
                        
                        # Colonnes pour l'agrégation
                        agg_cols = [col for col in actual_columns.values() if col in df_levee.columns]
                        
                        if agg_cols:
                            # Agrégation par région
                            df_region = df_levee.groupby('region')[agg_cols].sum().reset_index()
                            
                            # Création du graphique par région
                            fig_region = go.Figure()
                            
                            if 'parcelles terrain' in actual_columns and actual_columns['parcelles terrain'] in df_region.columns:
                                fig_region.add_trace(go.Bar(
                                    x=df_region['region'],
                                    y=df_region[actual_columns['parcelles terrain']],
                                    name='Parcelles Terrain',
                                    marker_color='royalblue'
                                ))
                            
                            if 'parcelles urm' in actual_columns and actual_columns['parcelles urm'] in df_region.columns:
                                fig_region.add_trace(go.Bar(
                                    x=df_region['region'],
                                    y=df_region[actual_columns['parcelles urm']],
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
                else:
                    st.warning("Colonnes de données parcelles non trouvées. Vérifiez la structure du fichier.")
                    st.write("Colonnes disponibles:", df_levee.columns.tolist())
                
                # Afficher la table de données
                with st.expander("📋 Voir les données"):
                    st.dataframe(df_filtre)
        else:
            st.error("Aucune donnée disponible pour l'analyse des levées par commune.")

    # Onglet 2: Évolution temporelle
    with tab2:
        st.subheader("📆 Évolution Temporelle des Levées")
        
        if not df_parcelles.empty:
            # Normalisation des noms de colonnes
            df_parcelles.columns = df_parcelles.columns.str.lower().str.strip()
            
            # Vérification des colonnes
            required_cols = ['date de debut', 'date de fin']
            available_cols = [col for col in required_cols if col in df_parcelles.columns]
            
            if not available_cols:
                st.warning("Colonnes de dates non trouvées dans le fichier.")
                st.write("Colonnes disponibles:", df_parcelles.columns.tolist())
            else:
                # Filtres
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'commune' in df_parcelles.columns:
                        commune_options = df_parcelles['commune'].dropna().unique()
                        commune_sel = st.selectbox("Filtrer par commune", ["Toutes"] + sorted(commune_options))
                    else:
                        commune_sel = "Toutes"
                
                with col2:
                    if 'lots' in df_parcelles.columns:
                        lot_options = df_parcelles['lots'].dropna().unique()
                        lot_sel = st.selectbox("Filtrer par lot", ["Tous"] + sorted(lot_options))
                    else:
                        lot_sel = "Tous"
                
                # Filtres temporels
                if 'date de debut' in df_parcelles.columns and 'date de fin' in df_parcelles.columns:
                    # Conversion sécurisée des dates
                    try:
                        df_parcelles['date de debut'] = pd.to_datetime(df_parcelles['date de debut'], errors='coerce')
                        df_parcelles['date de fin'] = pd.to_datetime(df_parcelles['date de fin'], errors='coerce')
                        
                        # Filtrer les lignes avec des dates valides
                        df_valid_dates = df_parcelles.dropna(subset=['date de debut', 'date de fin'])
                        
                        if df_valid_dates.empty:
                            st.warning("Aucune date valide trouvée dans les données.")
                        else:
                            date_min = df_valid_dates['date de debut'].min()
                            date_max = df_valid_dates['date de fin'].max()
                            
                            # Conversion en datetime python pour le slider
                            date_min = date_min.to_pydatetime()
                            date_max = date_max.to_pydatetime()
                            
                            date_range = st.slider(
                                "Période d'analyse",
                                min_value=date_min,
                                max_value=date_max,
                                value=(date_min, date_max),
                                format="YYYY-MM-DD"
                            )
                            
                            # Application des filtres
                            df_filtre = df_valid_dates[
                                (df_valid_dates['date de debut'] >= pd.Timestamp(date_range[0])) &
                                (df_valid_dates['date de fin'] <= pd.Timestamp(date_range[1]))
                            ]
                            
                            if commune_sel != "Toutes" and 'commune' in df_filtre.columns:
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
                                
                                if not evolution.empty:
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
                                else:
                                    st.warning("Aucune donnée d'évolution à afficher.")
                                
                                # Si la colonne "levee" existe, afficher l'évolution par type de levée
                                if 'levee' in df_filtre.columns:
                                    st.subheader("📊 Évolution par Type de Levée")
                                    
                                    levee_evolution = df_filtre.groupby(['periode', 'levee']).size().reset_index(name='nombre')
                                    
                                    if not levee_evolution.empty:
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
                                    else:
                                        st.warning("Aucune donnée d'évolution par type de levée à afficher.")
                                
                                # Afficher la table de données
                                with st.expander("📋 Voir les données"):
                                    st.dataframe(df_filtre)
                    except Exception as e:
                        st.error(f"Erreur lors du traitement des dates: {str(e)}")
                        st.write("Veuillez vérifier le format des dates dans le fichier.")
                else:
                    st.warning("Colonnes de dates nécessaires non trouvées.")
        else:
            st.error("Aucune donnée disponible pour l'analyse de l'évolution temporelle.")

    # Onglet 3: Post-traitement géométrique
    with tab3:
        st.subheader("📊 Analyse du Post-traitement Géométrique")
        
        if not df_post_traitement.empty:
            # Normalisation des noms de colonnes
            df_post_traitement.columns = df_post_traitement.columns.str.lower().str.strip()
            
            #st.write("Colonnes disponibles dans le fichier de post-traitement:", df_post_traitement.columns.tolist())
            
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
                num_cols = []
                for col in df_filtre.columns:
                    if df_filtre[col].dtype in ['int64', 'float64', 'Int64', 'Float64']:
                        # Vérifier si c'est une colonne de données de parcelles
                        if any(keyword in col.lower() for keyword in ['parcelle', 'total', 'nombre']):
                            num_cols.append(col)
                
                if num_cols:
                    st.write(f"Colonnes numériques trouvées: {num_cols}")
                    
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
                        df_agg = df_agg.reset_index()
                        df_agg[category_col] = "Sélection actuelle"
                    
                    # Graphique de comparaison
                    fig = go.Figure()
                    
                    for col in num_cols:
                        fig.add_trace(go.Bar(
                            x=df_agg[category_col],
                            y=df_agg[col],
                            name=col.replace('_', ' ').title(),
                        ))
                    
                    fig.update_layout(
                        title=f"Comparaison des parcelles par {category_col}",
                        xaxis_tickangle=-45,
                        xaxis_title=category_col.replace('_', ' ').title(),
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
                            'Type': [col.replace('nombre de parcelle ', '').replace('_', ' ').title() for col in pie_cols],
                            'Valeur': [df_filtre[col].sum() for col in pie_cols]
                        })
                        
                        # Filtrer les valeurs non nulles pour le graphique
                        pie_data = pie_data[pie_data['Valeur'] > 0]
                        
                        if not pie_data.empty:
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
                    
                    # Chercher les colonnes pertinentes avec des noms flexibles
                    received_col = None
                    processed_col = None
                    
                    for col in num_cols:
                        if 'reçue' in col or 'recu' in col or 'total' in col:
                            received_col = col
                        if 'post' in col and 'traité' in col:
                            processed_col = col
                    
                    if received_col and processed_col:
                        if 'lot' in df_filtre.columns:
                            # Par lot
                            df_lot = df_filtre.groupby('lot')[[received_col, processed_col]].sum().reset_index()
                            
                            fig_comp = go.Figure()
                            
                            fig_comp.add_trace(go.Bar(
                                x=df_lot['lot'],
                                y=df_lot[received_col],
                                name='Parcelles Reçues'
                            ))
                            
                            fig_comp.add_trace(go.Bar(
                                x=df_lot['lot'],
                                y=df_lot[processed_col],
                                name='Parcelles Post-traitées'
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
                        st.subheader("⚙️ Efficacité du Post-traitement")
                        
                        # Calculer le taux de traitement
                        df_filtre_calc = df_filtre.copy()
                        df_filtre_calc['taux_traitement'] = (df_filtre_calc[processed_col] / df_filtre_calc[received_col] * 100).fillna(0)
                        
                        # Agrégation par commune ou géométrie
                        if 'commune' in df_filtre_calc.columns:
                            agg_col = 'commune'
                        elif 'geom' in df_filtre_calc.columns:
                            agg_col = 'geom'
                        else:
                            agg_col = None
                        
                        if agg_col:
                            df_eff = df_filtre_calc.groupby(agg_col).agg({
                                received_col: 'sum',
                                processed_col: 'sum'
                            }).reset_index()
                            
                            # Éviter la division par zéro
                            df_eff['taux_traitement'] = df_eff.apply(
                                lambda row: (row[processed_col] / row[received_col] * 100) if row[received_col] > 0 else 0, 
                                axis=1
                            )
                            
                            fig_eff = px.bar(
                                df_eff,
                                x=agg_col,
                                y='taux_traitement',
                                text_auto='.1f',
                                title=f"Taux de traitement par {agg_col} (%)"
                            )
                            
                            fig_eff.update_traces(texttemplate='%{text}%', textposition='outside')
                            fig_eff.update_layout(
                                xaxis_title=agg_col.replace('_', ' ').title(),
                                yaxis_title="Taux de traitement (%)",
                                height=500
                            )
                            
                            st.plotly_chart(fig_eff, use_container_width=True)
                else:
                    st.warning("Aucune colonne numérique de parcelles trouvée dans les données.")
                
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
