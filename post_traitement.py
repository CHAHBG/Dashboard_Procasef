import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

@st.cache_data
def charger_levee_par_commune():
    try:
        df = pd.read_excel("data/Levee par commune Terrain_URM.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        df = df.fillna({'commune': 'Non spécifié'})
        return df
    except Exception as e:
        st.error(f"Erreur fichier levée commune : {e}")
        return pd.DataFrame()

@st.cache_data
def charger_parcelles_terrain_periode():
    try:
        df = pd.read_excel("data/Parcelles_terrain_periode.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        for col in ['date de debut', 'date de fin']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erreur fichier parcelles période : {e}")
        return pd.DataFrame()

@st.cache_data
def charger_parcelles_post_traitement():
    """Charge les données des parcelles post-traitées par géométrie"""
    try:
        df = pd.read_excel("data/Parcelles post traites par geom.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        
        # Conversion de dates si nécessaire
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Erreur fichier parcelles post-traitées : {e}")
        return pd.DataFrame()

def afficher_post_traitement(df_post_traitement=None):
    st.subheader("⚙️ Module de Post-traitement")

    df_levee = charger_levee_par_commune()
    df_parcelles = charger_parcelles_terrain_periode()
    df_post_traitement = charger_parcelles_post_traitement()

    # Création de 3 onglets pour le module
    tab1, tab2, tab3 = st.tabs(["🏘️ Communes & Régions", "📆 Par périodes", "📊 Post-traitement géométrique"])

    with tab1:
        st.markdown("### 📊 Comparaison des Parcelles Terrain vs URM")
        communes = df_levee['commune'].unique()
        commune_sel = st.selectbox("Filtrer par commune", ["Toutes"] + list(communes), key='commune_tab1')

        df_filtre = df_levee if commune_sel == "Toutes" else df_levee[df_levee['commune'] == commune_sel]

        if "parcelles terrain" in df_filtre.columns and "parcelles delimitées et enquetées (fourni par l'opérateur)(urm)" in df_filtre.columns:
            fig = go.Figure([
                go.Bar(name="Parcelles Terrain", x=df_filtre['commune'], y=df_filtre['parcelles terrain']),
                go.Bar(name="Parcelles URM", x=df_filtre['commune'], y=df_filtre["parcelles delimitées et enquetées (fourni par l'opérateur)(urm)"])
            ])
            fig.update_layout(barmode='group', xaxis_tickangle=-45,
                              title="Comparaison par commune", legend_title="Type")
            st.plotly_chart(fig, use_container_width=True)

            if 'region' in df_levee.columns:
                st.markdown("### 🌍 Comparaison par région")
                df_region = df_levee.groupby('region')[
                    ['parcelles terrain', "parcelles delimitées et enquetées (fourni par l'opérateur)(urm)"]
                ].sum().reset_index()

                fig2 = go.Figure([
                    go.Bar(name="Parcelles Terrain", x=df_region['region'], y=df_region['parcelles terrain']),
                    go.Bar(name="Parcelles URM", x=df_region['region'], y=df_region["parcelles delimitées et enquetées (fourni par l'opérateur)(urm)"])
                ])
                fig2.update_layout(barmode='group', xaxis_tickangle=-45,
                                   title="Comparaison par région", legend_title="Type")
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("### 📆 Évolution temporelle des levées")
        if df_parcelles.empty:
            st.warning("Aucune donnée disponible.")
            return

        commune_options = df_parcelles['commune'].dropna().unique()
        commune_sel = st.selectbox("Choisir une commune", ["Toutes"] + sorted(commune_options), key='commune_tab2')

        # Conversion explicite des dates
        date_min = df_parcelles['date de debut'].min()
        date_max = df_parcelles['date de fin'].max()

        # Vérification des dates valides
        if pd.isnull(date_min) or pd.isnull(date_max):
            st.warning("Dates invalides ou manquantes dans les données.")
            return

        date_min = pd.to_datetime(date_min).to_pydatetime()
        date_max = pd.to_datetime(date_max).to_pydatetime()

        if date_min >= date_max:
            st.warning("La date de début est postérieure à la date de fin.")
            return

        # Slider de dates corrigé
        date_range = st.slider(
            "Filtrer par période",
            min_value=date_min,
            max_value=date_max,
            value=(date_min, date_max),
            format="YYYY-MM-DD"
        )

        df_filtre = df_parcelles[
            (df_parcelles['date de debut'] >= date_range[0]) &
            (df_parcelles['date de fin'] <= date_range[1])
        ]
        if commune_sel != "Toutes":
            df_filtre = df_filtre[df_filtre['commune'] == commune_sel]

        if df_filtre.empty:
            st.warning("Aucune donnée pour cette sélection.")
            return

        df_filtre['periode'] = df_filtre['date de debut'].dt.to_period('M').astype(str)

        evolution = df_filtre.groupby('periode').size().reset_index(name='Nombre')
        fig = px.line(evolution, x='periode', y='Nombre', markers=True,
                      title="Évolution des levées par période")
        st.plotly_chart(fig, use_container_width=True)

        if 'statut' in df_filtre.columns:
            statuts = df_filtre.groupby(['periode', 'statut']).size().reset_index(name='count')
            fig2 = px.line(statuts, x='periode', y='count', color='statut', markers=True,
                           title="Évolution par statut")
            st.plotly_chart(fig2, use_container_width=True)

        with st.expander("📋 Voir les données filtrées"):
            st.dataframe(df_filtre)
            
    with tab3:
        st.markdown("### 📊 Analyse post-traitement géométrique")
        
        if df_post_traitement.empty:
            st.warning("Aucune donnée de post-traitement disponible.")
            return
            
        # Afficher les statistiques de base sur les parcelles post-traitées
        st.markdown("#### 📈 Statistiques générales")
        
        # Créer une colonne pour afficher les colonnes importantes et leurs statistiques
        col1, col2 = st.columns(2)
        
        # Nombre total de parcelles post-traitées
        with col1:
            total_parcelles = len(df_post_traitement)
            st.metric("Nombre total de parcelles", total_parcelles)
            
            # Vérifier si les colonnes de géométrie existent
            if 'superficie' in df_post_traitement.columns:
                superficie_moyenne = df_post_traitement['superficie'].mean()
                st.metric("Superficie moyenne (m²)", f"{superficie_moyenne:.2f}")
            
        with col2:
            # Vérifie si une colonne de statut existe (hypothèse basée sur le code existant)
            if 'statut' in df_post_traitement.columns:
                statut_counts = df_post_traitement['statut'].value_counts()
                fig = px.pie(
                    values=statut_counts.values,
                    names=statut_counts.index,
                    title="Répartition par statut"
                )
                st.plotly_chart(fig, use_container_width=True)
            elif 'etat' in df_post_traitement.columns:
                statut_counts = df_post_traitement['etat'].value_counts()
                fig = px.pie(
                    values=statut_counts.values,
                    names=statut_counts.index,
                    title="Répartition par état"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Filtres
        st.markdown("#### 🔍 Filtres")
        
        # Créer des filtres en fonction des colonnes disponibles
        col_filters = st.columns(3)
        
        filter_columns = []
        # Chercher des colonnes pertinentes pour le filtrage
        for col in df_post_traitement.columns:
            if col in ['commune', 'region', 'departement', 'statut', 'etat', 'type', 'categorie']:
                filter_columns.append(col)
        
        # Limiter à 3 colonnes au maximum pour éviter l'encombrement
        filter_columns = filter_columns[:3]
        
        # Créer les filtres
        selected_filters = {}
        for i, col in enumerate(filter_columns):
            with col_filters[i % 3]:
                unique_values = ["Tous"] + sorted(df_post_traitement[col].dropna().unique().tolist())
                selected_filters[col] = st.selectbox(f"Filtrer par {col}", unique_values, key=f'post_filter_{col}')
        
        # Appliquer les filtres
        df_filtered = df_post_traitement.copy()
        for col, value in selected_filters.items():
            if value != "Tous":
                df_filtered = df_filtered[df_filtered[col] == value]
        
        # Afficher les graphiques d'analyse
        st.markdown("#### 📊 Visualisations")
        
        # Déterminer quelles visualisations afficher en fonction des données disponibles
        chart_tabs = st.tabs(["Tendances temporelles", "Comparaisons", "Distribution"])
        
        with chart_tabs[0]:
            # Graphique de tendance temporelle (si des dates sont disponibles)
            date_cols = [col for col in df_filtered.columns if 'date' in col.lower()]
            if date_cols:
                selected_date_col = st.selectbox("Sélectionner une date", date_cols)
                if not pd.isna(df_filtered[selected_date_col]).all():
                    # Grouper par mois/année
                    df_filtered['mois_annee'] = df_filtered[selected_date_col].dt.to_period('M').astype(str)
                    evolution = df_filtered.groupby('mois_annee').size().reset_index(name='count')
                    
                    fig = px.line(evolution, x='mois_annee', y='count', markers=True,
                                title=f"Évolution par {selected_date_col}")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Pas de données valides pour la colonne '{selected_date_col}'")
            else:
                st.info("Aucune colonne de date disponible pour les tendances temporelles")
        
        with chart_tabs[1]:
            # Graphiques de comparaison
            comparison_cols = [col for col in filter_columns if len(df_filtered[col].unique()) > 1 and len(df_filtered[col].unique()) <= 10]
            if comparison_cols:
                selected_comp_col = st.selectbox("Comparer par", comparison_cols)
                
                # Déterminer une colonne numérique pour la comparaison
                numeric_cols = [col for col in df_filtered.columns if df_filtered[col].dtype in ['int64', 'float64']]
                if numeric_cols:
                    selected_metric = st.selectbox("Métrique", ["Compte"] + numeric_cols)
                    
                    if selected_metric == "Compte":
                        # Compter le nombre d'occurrences
                        comp_data = df_filtered[selected_comp_col].value_counts().reset_index()
                        comp_data.columns = [selected_comp_col, 'count']
                        
                        fig = px.bar(comp_data, x=selected_comp_col, y='count',
                                    title=f"Comparaison par {selected_comp_col}")
                    else:
                        # Utiliser une métrique numérique (somme, moyenne, etc.)
                        agg_method = st.radio("Méthode d'agrégation", ["Somme", "Moyenne", "Médiane", "Max", "Min"])
                        
                        if agg_method == "Somme":
                            comp_data = df_filtered.groupby(selected_comp_col)[selected_metric].sum().reset_index()
                        elif agg_method == "Moyenne":
                            comp_data = df_filtered.groupby(selected_comp_col)[selected_metric].mean().reset_index()
                        elif agg_method == "Médiane":
                            comp_data = df_filtered.groupby(selected_comp_col)[selected_metric].median().reset_index()
                        elif agg_method == "Max":
                            comp_data = df_filtered.groupby(selected_comp_col)[selected_metric].max().reset_index()
                        else:  # Min
                            comp_data = df_filtered.groupby(selected_comp_col)[selected_metric].min().reset_index()
                        
                        fig = px.bar(comp_data, x=selected_comp_col, y=selected_metric,
                                    title=f"{agg_method} de {selected_metric} par {selected_comp_col}")
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Aucune colonne numérique disponible pour les comparaisons")
            else:
                st.info("Pas assez de catégories distinctes pour les comparaisons")
        
        with chart_tabs[2]:
            # Distribution des valeurs numériques
            numeric_cols = [col for col in df_filtered.columns if df_filtered[col].dtype in ['int64', 'float64']]
            if numeric_cols:
                selected_dist_col = st.selectbox("Visualiser la distribution de", numeric_cols)
                
                fig = px.histogram(df_filtered, x=selected_dist_col,
                                title=f"Distribution de {selected_dist_col}")
                st.plotly_chart(fig, use_container_width=True)
                
                # Ajouter des statistiques descriptives
                stats = df_filtered[selected_dist_col].describe()
                st.write("Statistiques descriptives:")
                st.dataframe(stats)
            else:
                st.info("Aucune colonne numérique disponible pour l'analyse de distribution")
        
        # Afficher les données filtrées
        with st.expander("📋 Voir les données filtrées"):
            st.dataframe(df_filtered)
            
            # Option pour télécharger les données filtrées
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="Télécharger les données filtrées (CSV)",
                data=csv,
                file_name="parcelles_post_traitees_filtrees.csv",
                mime="text/csv",
            )

# Pour tester la fonction indépendamment (à commenter lors de l'intégration)
# if __name__ == "__main__":
#     st.set_page_config(page_title="Test Module Post-traitement", layout="wide")
#     afficher_post_traitement()
