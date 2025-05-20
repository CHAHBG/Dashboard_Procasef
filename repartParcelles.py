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
    # Statistiques globales toujours visibles en haut de la page
    st.header("📊 Tableau de Bord des Parcelles")
    
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nombre total de parcelles", len(df_parcelles))
        col2.metric("Parcelles NICAD", (df_parcelles["nicad"] == "Avec NICAD").sum())
        col3.metric("Parcelles délibérées (🔄)", (df_parcelles["statut_deliberation"] == "Délibérée").sum())
        col4.metric("Superficie totale (m²)", f"{df_parcelles['superficie'].sum():,.2f}")
    
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
            fig_global_nicad = px.pie(
                df_parcelles, 
                names="nicad", 
                title="Répartition globale des parcelles NICAD",
                labels={"nicad": "Statut NICAD"}
            )
            st.plotly_chart(fig_global_nicad, use_container_width=True)
        
        with col_deliberation:
            # Répartition délibération
            fig_global_deliberation = px.pie(
                df_parcelles, 
                names="statut_deliberation",
                title="Répartition des parcelles délibérées",
                labels={"statut_deliberation": "Statut délibération"}
            )
            st.plotly_chart(fig_global_deliberation, use_container_width=True)
        
        # Relation NICAD et délibération
        st.subheader("🔄 Relation entre NICAD et délibération")
        nicad_delib_data = df_parcelles.groupby(["nicad", "statut_deliberation"]).size().reset_index(
            name="Nombre de parcelles")
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
        
        # Répartition par usage
        if "type_usag" in df_parcelles.columns:
            st.subheader("🏗️ Répartition par usage des parcelles")
            
            col_usage, col_usage_delib = st.columns(2)
            
            with col_usage:
                fig_usage = px.pie(
                    df_parcelles, 
                    names="type_usag", 
                    title="Répartition des usages",
                    labels={"type_usag": "Usage"}
                )
                st.plotly_chart(fig_usage, use_container_width=True)
            
            with col_usage_delib:
                # Graphique montrant la répartition des délibérations par type d'usage
                usage_delib_data = df_parcelles.groupby(["type_usag", "statut_deliberation"]).size().reset_index(
                    name="Nombre")
                fig_usage_delib = px.bar(
                    usage_delib_data, 
                    x="type_usag", 
                    y="Nombre", 
                    color="statut_deliberation",
                    barmode="group", 
                    title="Délibération par type d'usage",
                    labels={"type_usag": "Usage", "statut_deliberation": "Statut délibération"}
                )
                st.plotly_chart(fig_usage_delib, use_container_width=True)
    
    # ===== TAB 2: ANALYSE PAR COMMUNE =====
    with tab_par_commune:
        # Sous-onglets pour l'analyse par commune
        subtab_repart, subtab_taux = st.tabs(["📊 Répartition des parcelles", "📈 Taux de délibération"])
        
        with subtab_repart:
            # Onglets pour choisir entre la vue NICAD et la vue délibération
            vue_commune = st.radio("Choisir la vue :", ["NICAD par commune", "Délibération par commune"])

            if vue_commune == "NICAD par commune":
                commune_nicad_data = df_parcelles.groupby(["commune", "nicad"]).size().reset_index(
                    name="Nombre de parcelles")
                fig_commune_nicad = px.bar(
                    commune_nicad_data, 
                    x="commune", 
                    y="Nombre de parcelles", 
                    color="nicad",
                    barmode="group", 
                    title="Parcelles avec/sans NICAD par commune",
                    labels={"nicad": "NICAD"}
                )
                st.plotly_chart(fig_commune_nicad, use_container_width=True)
            else:
                commune_delib_data = df_parcelles.groupby(["commune", "statut_deliberation"]).size().reset_index(
                    name="Nombre de parcelles")
                fig_commune_delib = px.bar(
                    commune_delib_data, 
                    x="commune", 
                    y="Nombre de parcelles",
                    color="statut_deliberation",
                    barmode="group", 
                    title="Parcelles délibérées/non délibérées par commune",
                    labels={"statut_deliberation": "Statut délibération"}
                )
                st.plotly_chart(fig_commune_delib, use_container_width=True)
        
        with subtab_taux:
            # Calculer le taux de délibération par commune
            taux_delib_liste = []
            for commune in df_parcelles['commune'].unique():
                df_commune = df_parcelles[df_parcelles['commune'] == commune]
                total_parcelles = len(df_commune)
                parcelles_deliberees = (df_commune["statut_deliberation"] == "Délibérée").sum()
                taux = (parcelles_deliberees / total_parcelles * 100) if total_parcelles > 0 else 0
                taux_delib_liste.append({"commune": commune, "Taux de délibération (%)": taux})

            taux_delib = pd.DataFrame(taux_delib_liste)

            # Trier par taux décroissant
            taux_delib = taux_delib.sort_values(by="Taux de délibération (%)", ascending=False)

            fig_taux_delib = px.bar(
                taux_delib, 
                x="commune", 
                y="Taux de délibération (%)",
                title="Taux de délibération par commune (%)",
                color="Taux de délibération (%)",
                color_continuous_scale=["red", "orange", "green"],
                labels={"commune": "Commune"}
            )

            st.plotly_chart(fig_taux_delib, use_container_width=True)

    # ===== TAB 3: ANALYSE DÉTAILLÉE =====
    with tab_details:
        communes = ["Toutes"] + sorted(df_parcelles["commune"].dropna().unique())
        commune_selectionnee = st.selectbox("🏘️ Choisir une commune :", communes)

        if commune_selectionnee != "Toutes":
            df_filtre = df_parcelles[df_parcelles["commune"] == commune_selectionnee]
            villages = ["Tous"] + sorted(df_filtre["village"].dropna().unique())
        else:
            df_filtre = df_parcelles
            villages = ["Tous"] + sorted(df_parcelles["village"].dropna().unique())

        village_selectionne = st.selectbox("📍 Choisir un village :", villages)

        if village_selectionne != "Tous":
            df_filtre = df_filtre[df_filtre["village"] == village_selectionne]

        st.subheader(f"📍 Statistiques pour : {village_selectionne if village_selectionne != 'Tous' else 'Tous les villages'} ({commune_selectionnee if commune_selectionnee != 'Toutes' else 'Toutes les communes'})")
        
        # Métriques pour la sélection
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total parcelles", len(df_filtre))
        col2.metric("Parcelles NICAD", (df_filtre["nicad"] == "Avec NICAD").sum())
        col3.metric("Parcelles délibérées", (df_filtre["statut_deliberation"] == "Délibérée").sum())
        col4.metric("Superficie totale", f"{df_filtre['superficie'].sum():,.2f}")

        # Sous-onglets pour les graphiques
        subtab_nicad, subtab_delib = st.tabs(["📊 Répartition NICAD", "🔄 Répartition Délibération"])

        with subtab_nicad:
            fig_village_nicad = px.pie(
                df_filtre, 
                names="nicad", 
                title="Répartition NICAD - Données filtrées",
                labels={"nicad": "NICAD"}
            )
            st.plotly_chart(fig_village_nicad, use_container_width=True)

        with subtab_delib:
            fig_village_delib = px.pie(
                df_filtre, 
                names="statut_deliberation",
                title="Répartition délibération - Données filtrées",
                labels={"statut_deliberation": "Délibération"}
            )
            st.plotly_chart(fig_village_delib, use_container_width=True)

    # ===== TAB 4: DONNÉES =====
    with tab_donnees:
        st.subheader("🧾 Données filtrées")
        
        # Options de filtrage supplémentaires
        col_nicad_filter, col_delib_filter = st.columns(2)
        
        with col_nicad_filter:
            nicad_filter = st.multiselect(
                "Filtrer par statut NICAD :",
                options=df_parcelles["nicad"].unique(),
                default=df_parcelles["nicad"].unique()
            )
        
        with col_delib_filter:
            delib_filter = st.multiselect(
                "Filtrer par statut délibération :",
                options=df_parcelles["statut_deliberation"].unique(),
                default=df_parcelles["statut_deliberation"].unique()
            )
        
        # Application des filtres
        df_filtre_final = df_parcelles[
            (df_parcelles["nicad"].isin(nicad_filter)) & 
            (df_parcelles["statut_deliberation"].isin(delib_filter))
        ]
        
        # Sélection des colonnes à afficher
        colonnes_affichees = ["commune", "village", "nicad", "statut_deliberation", "superficie"]
        if "type_usag" in df_parcelles.columns:
            colonnes_affichees.append("type_usag")
        
        # Affichage du tableau filtré
        st.dataframe(df_filtre_final[colonnes_affichees], use_container_width=True)


# Exemple d'utilisation
    
    # Chargement des données (exemple)
    # Remplacer cette partie par votre propre chargement de données
    try:
        df_parcelles = pd.read_csv("parcelles.csv")
        # Conversion des colonnes si nécessaire
        if "superficie" not in df_parcelles.columns:
            df_parcelles["superficie"] = 0.0
        else:
            df_parcelles["superficie"] = pd.to_numeric(df_parcelles["superficie"], errors="coerce").fillna(0)
        
        if "nicad" not in df_parcelles.columns:
            df_parcelles["nicad"] = "Sans NICAD"
        
        if "statut_deliberation" not in df_parcelles.columns:
            df_parcelles["statut_deliberation"] = "Non délibérée"
        
        # Appel de la fonction principale
        afficher_dashboard_parcelles(df_parcelles)
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        st.info("Veuillez charger un fichier CSV contenant les données des parcelles.")
