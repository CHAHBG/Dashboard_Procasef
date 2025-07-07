import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def afficher_dashboard_parcelles(df_parcelles):
    """
    Affiche le tableau de bord des parcelles organisé en onglets

    Args:
        df_parcelles (DataFrame): Dataframe contenant les données des parcelles
    """
    # Vérifier si le DataFrame est vide
    if df_parcelles.empty:
        st.warning("⚠️ Aucune donnée de parcelles disponible. Veuillez télécharger un fichier de données.")
        return

    # Statistiques globales toujours visibles en haut de la page
    st.header("📊 Tableau de Bord des Parcelles")

    # Vérifier la présence des colonnes nécessaires
    required_columns = ['nicad', 'statut_deliberation', 'superficie']
    missing_columns = [col for col in required_columns if col not in df_parcelles.columns]

    if missing_columns:
        st.error(f"❌ Colonnes manquantes dans les données: {missing_columns}")
        st.info("Les colonnes suivantes sont requises: nicad, statut_deliberation, superficie")
        return

    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        # Calculer les métriques avec gestion des erreurs
        total_parcelles = len(df_parcelles)

        try:
            parcelles_nicad = (df_parcelles["nicad"] == "Avec NICAD").sum()
        except:
            parcelles_nicad = 0

        try:
            parcelles_deliberees = (df_parcelles["statut_deliberation"] == "Délibérée").sum()
        except:
            parcelles_deliberees = 0

        try:
            superficie_totale = df_parcelles['superficie'].sum()
        except:
            superficie_totale = 0

        col1.metric("Nombre total de parcelles", total_parcelles)
        col2.metric("Parcelles NICAD", parcelles_nicad)
        col3.metric("Parcelles délibérées", parcelles_deliberees)
        col4.metric("Superficie totale (m²)", f"{superficie_totale:,.2f}")

    # Création des onglets principaux
    tab_vue_globale, tab_par_commune, tab_details, tab_donnees = st.tabs([
        "🌍 Vue Globale",
        "🏘️ Analyse par Commune",
        "📍 Analyse Détaillée",
        "🧾 Données"
    ])

    # ===== TAB 1: VUE GLOBALE =====
    with tab_vue_globale:
        col_nicad, col_deliberation = st.columns(2)

        with col_nicad:
            # Répartition NICAD
            if 'nicad' in df_parcelles.columns and not df_parcelles['nicad'].empty:
                fig_global_nicad = px.pie(
                    df_parcelles,
                    names="nicad",
                    title="Répartition globale des parcelles NICAD",
                    labels={"nicad": "Statut NICAD"}
                )
                fig_global_nicad.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                fig_global_nicad.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.05
                    )
                )
                st.plotly_chart(fig_global_nicad, use_container_width=True)
            else:
                st.info("Données NICAD non disponibles")

        with col_deliberation:
            # Répartition délibération
            if 'statut_deliberation' in df_parcelles.columns and not df_parcelles['statut_deliberation'].empty:
                fig_global_deliberation = px.pie(
                    df_parcelles,
                    names="statut_deliberation",
                    title="Répartition des parcelles délibérées",
                    labels={"statut_deliberation": "Statut délibération"}
                )
                fig_global_deliberation.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                fig_global_deliberation.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.05
                    )
                )
                st.plotly_chart(fig_global_deliberation, use_container_width=True)
            else:
                st.info("Données de délibération non disponibles")

        # Relation NICAD et délibération
        if 'nicad' in df_parcelles.columns and 'statut_deliberation' in df_parcelles.columns:
            st.subheader("🔄 Relation entre NICAD et délibération")
            nicad_delib_data = df_parcelles.groupby(["nicad", "statut_deliberation"]).size().reset_index(
                name="Nombre de parcelles")

            if not nicad_delib_data.empty:
                fig_relation = px.bar(
                    nicad_delib_data,
                    x="nicad",
                    y="Nombre de parcelles",
                    color="statut_deliberation",
                    barmode="group",
                    title="Relation entre statut NICAD et délibération",
                    labels={"nicad": "Statut NICAD", "statut_deliberation": "Statut délibération"}
                )
                st.plotly_chart(fig_relation, use_container_width=True)
            else:
                st.info("Données insuffisantes pour afficher la relation NICAD/délibération")

        # Répartition par usage
        if "type_usag" in df_parcelles.columns and not df_parcelles["type_usag"].empty:
            st.subheader("🏗️ Répartition par usage des parcelles")

            # Option pour choisir le type de visualisation
            type_viz_usage = st.radio(
                "Type de visualisation :",
                ["Graphique en secteurs", "Graphique en barres"],
                key="viz_usage_global"
            )

            col_usage, col_usage_delib = st.columns(2)

            with col_usage:
                if type_viz_usage == "Graphique en secteurs":
                    # Calculer les pourcentages pour affichage personnalisé
                    usage_counts = df_parcelles["type_usag"].value_counts()
                    usage_percentages = (usage_counts / len(df_parcelles) * 100).round(1)

                    fig_usage = px.pie(
                        values=usage_counts.values,
                        names=usage_counts.index,
                        title="Répartition des usages"
                    )

                    # Configuration améliorée pour les labels
                    fig_usage.update_traces(
                        textposition='auto',
                        textinfo='label+percent',
                        textfont_size=10,
                        pull=[0.05 if val < usage_counts.max() * 0.1 else 0 for val in usage_counts.values]
                        # Séparer les petites parts
                    )

                    fig_usage.update_layout(
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05,
                            font=dict(size=10)
                        ),
                        margin=dict(l=20, r=120, t=50, b=20),
                        height=400
                    )

                else:
                    # Graphique en barres horizontal pour plus de lisibilité
                    usage_counts = df_parcelles["type_usag"].value_counts().reset_index()
                    usage_counts.columns = ['Usage', 'Nombre']

                    fig_usage = px.bar(
                        usage_counts,
                        x='Nombre',
                        y='Usage',
                        orientation='h',
                        title="Répartition des usages",
                        text='Nombre'
                    )
                    fig_usage.update_traces(texttemplate='%{text}', textposition='outside')
                    fig_usage.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})

                st.plotly_chart(fig_usage, use_container_width=True)

            with col_usage_delib:
                # Graphique montrant la répartition des délibérations par type d'usage
                if 'statut_deliberation' in df_parcelles.columns:
                    usage_delib_data = df_parcelles.groupby(["type_usag", "statut_deliberation"]).size().reset_index(
                        name="Nombre")

                    if not usage_delib_data.empty:
                        fig_usage_delib = px.bar(
                            usage_delib_data,
                            x="type_usag",
                            y="Nombre",
                            color="statut_deliberation",
                            barmode="group",title="Délibération par type d'usage",
                            labels={"type_usag": "Type d'usage", "statut_deliberation": "Statut délibération"}
                        )
                        fig_usage_delib.update_xaxes(tickangle=45)
                        st.plotly_chart(fig_usage_delib, use_container_width=True)
                    else:
                        st.info("Données insuffisantes pour afficher la délibération par usage")
                else:
                    st.info("Données de délibération non disponibles")
    
    # ===== TAB 2: ANALYSE PAR COMMUNE =====
    with tab_par_commune:
        if 'commune' in df_parcelles.columns and not df_parcelles['commune'].empty:
            st.subheader("🏘️ Analyse par commune")
            
            # Sélection de la commune
            communes_list = ['Toutes les communes'] + sorted(df_parcelles['commune'].unique().tolist())
            commune_selectionnee = st.selectbox("Sélectionnez une commune :", communes_list)
            
            # Filtrer les données selon la commune sélectionnée
            if commune_selectionnee != 'Toutes les communes':
                df_filtered = df_parcelles[df_parcelles['commune'] == commune_selectionnee]
            else:
                df_filtered = df_parcelles
            
            # Métriques pour la commune sélectionnée
            col1, col2, col3, col4 = st.columns(4)
            
            total_parcelles_commune = len(df_filtered)
            parcelles_nicad_commune = (df_filtered["nicad"] == "Avec NICAD").sum() if 'nicad' in df_filtered.columns else 0
            parcelles_deliberees_commune = (df_filtered["statut_deliberation"] == "Délibérée").sum() if 'statut_deliberation' in df_filtered.columns else 0
            superficie_commune = df_filtered['superficie'].sum() if 'superficie' in df_filtered.columns else 0
            
            col1.metric("Parcelles", total_parcelles_commune)
            col2.metric("NICAD", parcelles_nicad_commune)
            col3.metric("Délibérées", parcelles_deliberees_commune)
            col4.metric("Superficie (m²)", f"{superficie_commune:,.2f}")
            
            # Graphiques par commune
            if commune_selectionnee == 'Toutes les communes':
                # Vue comparative entre toutes les communes
                col_commune1, col_commune2 = st.columns(2)
                
                with col_commune1:
                    # Nombre de parcelles par commune
                    parcelles_par_commune = df_parcelles['commune'].value_counts().reset_index()
                    parcelles_par_commune.columns = ['Commune', 'Nombre de parcelles']
                    
                    fig_communes = px.bar(
                        parcelles_par_commune.head(10),  # Top 10 communes
                        x='Commune',
                        y='Nombre de parcelles',
                        title="Top 10 communes par nombre de parcelles"
                    )
                    fig_communes.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_communes, use_container_width=True)
                
                with col_commune2:
                    # Superficie par commune
                    if 'superficie' in df_parcelles.columns:
                        superficie_par_commune = df_parcelles.groupby('commune')['superficie'].sum().reset_index()
                        superficie_par_commune = superficie_par_commune.sort_values('superficie', ascending=False).head(10)
                        
                        fig_superficie = px.bar(
                            superficie_par_commune,
                            x='commune',
                            y='superficie',
                            title="Top 10 communes par superficie totale"
                        )
                        fig_superficie.update_xaxes(tickangle=45)
                        st.plotly_chart(fig_superficie, use_container_width=True)
                    else:
                        st.info("Données de superficie non disponibles")
                
                # Tableau récapitulatif par commune
                st.subheader("📋 Récapitulatif par commune")
                summary_commune = df_parcelles.groupby('commune').agg({
                    'nicad': lambda x: (x == "Avec NICAD").sum() if 'nicad' in df_parcelles.columns else 0,
                    'statut_deliberation': lambda x: (x == "Délibérée").sum() if 'statut_deliberation' in df_parcelles.columns else 0,
                    'superficie': 'sum' if 'superficie' in df_parcelles.columns else lambda x: 0
                }).reset_index()
                
                summary_commune.columns = ['Commune', 'Parcelles NICAD', 'Parcelles délibérées', 'Superficie totale']
                summary_commune['Nombre total parcelles'] = df_parcelles['commune'].value_counts().values
                
                # Réorganiser les colonnes
                summary_commune = summary_commune[['Commune', 'Nombre total parcelles', 'Parcelles NICAD', 'Parcelles délibérées', 'Superficie totale']]
                summary_commune = summary_commune.sort_values('Nombre total parcelles', ascending=False)
                
                st.dataframe(summary_commune, use_container_width=True)
            
            else:
                # Vue détaillée pour une commune spécifique
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    # Répartition NICAD pour la commune
                    if 'nicad' in df_filtered.columns and not df_filtered['nicad'].empty:
                        fig_nicad_commune = px.pie(
                            df_filtered,
                            names="nicad",
                            title=f"Répartition NICAD - {commune_selectionnee}"
                        )
                        st.plotly_chart(fig_nicad_commune, use_container_width=True)
                    else:
                        st.info("Données NICAD non disponibles pour cette commune")
                
                with col_detail2:
                    # Répartition délibération pour la commune
                    if 'statut_deliberation' in df_filtered.columns and not df_filtered['statut_deliberation'].empty:
                        fig_delib_commune = px.pie(
                            df_filtered,
                            names="statut_deliberation",
                            title=f"Répartition délibération - {commune_selectionnee}"
                        )
                        st.plotly_chart(fig_delib_commune, use_container_width=True)
                    else:
                        st.info("Données de délibération non disponibles pour cette commune")
                
                # Répartition par usage pour la commune
                if 'type_usag' in df_filtered.columns and not df_filtered['type_usag'].empty:
                    st.subheader(f"🏗️ Répartition par usage - {commune_selectionnee}")
                    
                    usage_commune = df_filtered['type_usag'].value_counts().reset_index()
                    usage_commune.columns = ['Usage', 'Nombre']
                    
                    fig_usage_commune = px.bar(
                        usage_commune,
                        x='Usage',
                        y='Nombre',
                        title=f"Répartition des usages - {commune_selectionnee}"
                    )
                    fig_usage_commune.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_usage_commune, use_container_width=True)
        
        else:
            st.info("Données de commune non disponibles")
    
    # ===== TAB 3: ANALYSE DÉTAILLÉE =====
    with tab_details:
        st.subheader("📍 Analyse détaillée")
        
        # Filtres interactifs
        st.sidebar.header("🔍 Filtres")
        
        # Filtre par commune
        if 'commune' in df_parcelles.columns:
            communes_filtre = st.sidebar.multiselect(
                "Communes",
                options=df_parcelles['commune'].unique(),
                default=df_parcelles['commune'].unique()
            )
            df_filtered_details = df_parcelles[df_parcelles['commune'].isin(communes_filtre)]
        else:
            df_filtered_details = df_parcelles
        
        # Filtre par NICAD
        if 'nicad' in df_parcelles.columns:
            nicad_filtre = st.sidebar.multiselect(
                "Statut NICAD",
                options=df_parcelles['nicad'].unique(),
                default=df_parcelles['nicad'].unique()
            )
            df_filtered_details = df_filtered_details[df_filtered_details['nicad'].isin(nicad_filtre)]
        
        # Filtre par délibération
        if 'statut_deliberation' in df_parcelles.columns:
            deliberation_filtre = st.sidebar.multiselect(
                "Statut délibération",
                options=df_parcelles['statut_deliberation'].unique(),
                default=df_parcelles['statut_deliberation'].unique()
            )
            df_filtered_details = df_filtered_details[df_filtered_details['statut_deliberation'].isin(deliberation_filtre)]
        
        # Filtre par usage
        if 'type_usag' in df_parcelles.columns:
            usage_filtre = st.sidebar.multiselect(
                "Type d'usage",
                options=df_parcelles['type_usag'].unique(),
                default=df_parcelles['type_usag'].unique()
            )
            df_filtered_details = df_filtered_details[df_filtered_details['type_usag'].isin(usage_filtre)]
        
        # Filtre par superficie
        if 'superficie' in df_parcelles.columns:
            superficie_min = float(df_parcelles['superficie'].min())
            superficie_max = float(df_parcelles['superficie'].max())
            superficie_range = st.sidebar.slider(
                "Superficie (m²)",
                min_value=superficie_min,
                max_value=superficie_max,
                value=(superficie_min, superficie_max)
            )
            df_filtered_details = df_filtered_details[
                (df_filtered_details['superficie'] >= superficie_range[0]) & 
                (df_filtered_details['superficie'] <= superficie_range[1])
            ]
        
        # Affichage des résultats filtrés
        st.write(f"**Nombre de parcelles après filtrage : {len(df_filtered_details)}**")
        
        if len(df_filtered_details) > 0:
            # Métriques des données filtrées
            col1, col2, col3, col4 = st.columns(4)
            
            total_filtrees = len(df_filtered_details)
            nicad_filtrees = (df_filtered_details["nicad"] == "Avec NICAD").sum() if 'nicad' in df_filtered_details.columns else 0
            deliberees_filtrees = (df_filtered_details["statut_deliberation"] == "Délibérée").sum() if 'statut_deliberation' in df_filtered_details.columns else 0
            superficie_filtrees = df_filtered_details['superficie'].sum() if 'superficie' in df_filtered_details.columns else 0
            
            col1.metric("Total", total_filtrees)
            col2.metric("NICAD", nicad_filtrees)
            col3.metric("Délibérées", deliberees_filtrees)
            col4.metric("Superficie", f"{superficie_filtrees:,.2f} m²")
            
            # Graphiques des données filtrées
            if len(df_filtered_details) > 1:
                col_graph1, col_graph2 = st.columns(2)
                
                with col_graph1:
                    # Distribution des superficies
                    if 'superficie' in df_filtered_details.columns:
                        fig_hist = px.histogram(
                            df_filtered_details,
                            x='superficie',
                            nbins=20,
                            title="Distribution des superficies (données filtrées)"
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
                
                with col_graph2:
                    # Analyse croisée
                    if 'nicad' in df_filtered_details.columns and 'statut_deliberation' in df_filtered_details.columns:
                        crosstab = pd.crosstab(df_filtered_details['nicad'], df_filtered_details['statut_deliberation'])
                        fig_heatmap = px.imshow(
                            crosstab,
                            text_auto=True,
                            aspect="auto",
                            title="Analyse croisée NICAD vs Délibération"
                        )
                        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        else:
            st.warning("Aucune parcelle ne correspond aux filtres sélectionnés.")
    
    # ===== TAB 4: DONNÉES =====
    with tab_donnees:
        st.subheader("🧾 Données brutes")
        
        # Options d'affichage
        col_options1, col_options2 = st.columns(2)
        
        with col_options1:
            nb_lignes = st.selectbox(
                "Nombre de lignes à afficher",
                options=[10, 25, 50, 100, len(df_parcelles)],
                index=1
            )
        
        with col_options2:
            if st.button("📥 Télécharger les données (CSV)"):
                csv = df_parcelles.to_csv(index=False)
                st.download_button(
                    label="Télécharger CSV",
                    data=csv,
                    file_name="parcelles_data.csv",
                    mime="text/csv"
                )
        
        # Affichage du tableau
        st.dataframe(df_parcelles.head(nb_lignes), use_container_width=True)
        
        # Informations sur les données
        st.subheader("ℹ️ Informations sur les données")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.write("**Dimensions du dataset :**")
            st.write(f"- Nombre de lignes : {len(df_parcelles)}")
            st.write(f"- Nombre de colonnes : {len(df_parcelles.columns)}")
        
        with col_info2:
            st.write("**Colonnes disponibles :**")
            for col in df_parcelles.columns:
                st.write(f"- {col}")
        
        # Statistiques descriptives
        if st.checkbox("Afficher les statistiques descriptives"):
            st.subheader("📊 Statistiques descriptives")
            
            # Sélection des colonnes numériques
            numeric_columns = df_parcelles.select_dtypes(include=['number']).columns
            
            if len(numeric_columns) > 0:
                selected_columns = st.multiselect(
                    "Sélectionnez les colonnes numériques à analyser",
                    options=numeric_columns,
                    default=numeric_columns[:3] if len(numeric_columns) >= 3 else numeric_columns
                )
                
                if selected_columns:
                    st.dataframe(df_parcelles[selected_columns].describe(), use_container_width=True)
                else:
                    st.info("Sélectionnez au moins une colonne numérique")
            else:
                st.info("Aucune colonne numérique disponible pour les statistiques")
        
        # Vérification de la qualité des données
        if st.checkbox("Vérifier la qualité des données"):
            st.subheader("🔍 Qualité des données")
            
            # Valeurs manquantes
            missing_data = df_parcelles.isnull().sum()
            missing_percentage = (missing_data / len(df_parcelles)) * 100
            
            quality_df = pd.DataFrame({
                'Colonne': missing_data.index,
                'Valeurs manquantes': missing_data.values,
                'Pourcentage': missing_percentage.values
            })
            
            quality_df = quality_df[quality_df['Valeurs manquantes'] > 0]
            
            if len(quality_df) > 0:
                st.warning("⚠️ Valeurs manquantes détectées :")
                st.dataframe(quality_df, use_container_width=True)
            else:
                st.success("✅ Aucune valeur manquante détectée")
            
            # Doublons
            nb_doublons = df_parcelles.duplicated().sum()
            if nb_doublons > 0:
                st.warning(f"⚠️ {nb_doublons} lignes dupliquées détectées")
            else:
                st.success("✅ Aucune ligne dupliquée détectée")


# Fonction utilitaire pour le préprocessing des données
def preprocess_parcelles_data(df):
    """
    Préprocesse les données des parcelles pour le dashboard
    
    Args:
        df (DataFrame): Dataframe brut des parcelles
        
    Returns:
        DataFrame: Dataframe préprocessé
    """
    # Copie du dataframe pour éviter les modifications du dataframe original
    df_processed = df.copy()
    
    # Nettoyage des colonnes de texte
    text_columns = df_processed.select_dtypes(include=['object']).columns
    for col in text_columns:
        df_processed[col] = df_processed[col].astype(str).str.strip()
    
    # Conversion des colonnes numériques
    numeric_columns = ['superficie']
    for col in numeric_columns:
        if col in df_processed.columns:
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
    
    # Normalisation des valeurs catégorielles
    categorical_mappings = {
        'nicad': {'1': 'Avec NICAD', '0': 'Sans NICAD', 'True': 'Avec NICAD', 'False': 'Sans NICAD'},
        'statut_deliberation': {'1': 'Délibérée', '0': 'Non délibérée', 'True': 'Délibérée', 'False': 'Non délibérée'}
    }
    
    for col, mapping in categorical_mappings.items():
        if col in df_processed.columns:
            df_processed[col] = df_processed[col].map(mapping).fillna(df_processed[col])
    
    return df_processed


# Fonction principale pour lancer le dashboard
def main():
    """
    Fonction principale pour lancer le dashboard des parcelles
    """
    st.set_page_config(
        page_title="Dashboard Parcelles",
        page_icon="🏘️",
        layout="wide"
    )
    
    # Titre principal
    st.title("🏘️ Dashboard de Gestion des Parcelles")
    
    # Upload de fichier
    uploaded_file = st.file_uploader(
        "Choisissez un fichier de données des parcelles",
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        try:
            # Lecture du fichier
            if uploaded_file.name.endswith('.csv'):
                df_parcelles = pd.read_csv(uploaded_file)
            else:
                df_parcelles = pd.read_excel(uploaded_file)
            
            # Préprocessing des données
            df_parcelles = preprocess_parcelles_data(df_parcelles)
            
            # Affichage du dashboard
            afficher_dashboard_parcelles(df_parcelles)
            
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier : {str(e)}")
            st.info("Veuillez vérifier le format de votre fichier et réessayer.")
    
    else:
        st.info("👆 Veuillez télécharger un fichier de données pour commencer l'analyse.")
        
        # Affichage d'un exemple de structure de données attendue
        st.subheader("📋 Structure de données attendue")
        st.write("Votre fichier doit contenir au minimum les colonnes suivantes :")
        
        exemple_data = {
            'nicad': ['Avec NICAD', 'Sans NICAD', 'Avec NICAD'],
            'statut_deliberation': ['Délibérée', 'Non délibérée', 'Délibérée'],
            'superficie': [1200.5, 800.0, 1500.2],
            'commune': ['Commune A', 'Commune B', 'Commune A'],
            'type_usag': ['Résidentiel', 'Commercial', 'Industriel']
        }
        
        df_exemple = pd.DataFrame(exemple_data)
        st.dataframe(df_exemple, use_container_width=True)


if __name__ == "__main__":
    main()
