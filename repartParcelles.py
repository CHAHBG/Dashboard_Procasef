import streamlit as st
import pandas as pd
import plotly.express as px

def afficher_dashboard_parcelles(df_parcelles):
    st.header("📊 Tableau de Bord des Parcelles")

    # Vérification de la présence des colonnes essentielles
    colonnes_essentielles = ["nicad", "statut_deliberation", "superficie", "commune", "village"]
    for col in colonnes_essentielles:
        if col not in df_parcelles.columns:
            st.error(f"Colonne manquante : {col}")
            st.stop()

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nombre total de parcelles", len(df_parcelles))
        col2.metric("Parcelles NICAD", (df_parcelles["nicad"] == "Avec NICAD").sum())
        col3.metric("Parcelles délibérées (🔄)", (df_parcelles["statut_deliberation"] == "Délibérée").sum())
        col4.metric("Superficie totale (m²)", f"{df_parcelles['superficie'].sum():,.2f}")

    tab_vue_globale, tab_par_commune, tab_details, tab_donnees = st.tabs([
        "🌍 Vue Globale",
        "🏘️ Analyse par Commune",
        "📍 Analyse Détaillée",
        "🧾 Données"
    ])

    # TAB 1 : Vue globale
    with tab_vue_globale:
        col_nicad, col_deliberation = st.columns(2)
        with col_nicad:
            fig_global_nicad = px.pie(
                df_parcelles,
                names="nicad",
                title="Répartition globale des parcelles NICAD",
                labels={"nicad": "Statut NICAD"}
            )
            st.plotly_chart(fig_global_nicad, use_container_width=True)
        with col_deliberation:
            fig_global_deliberation = px.pie(
                df_parcelles,
                names="statut_deliberation",
                title="Répartition des parcelles délibérées",
                labels={"statut_deliberation": "Statut délibération"}
            )
            st.plotly_chart(fig_global_deliberation, use_container_width=True)
        st.subheader("🔄 Relation entre NICAD et délibération")
        nicad_delib_data = df_parcelles.groupby(["nicad", "statut_deliberation"]).size().reset_index(name="Nombre de parcelles")
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

    # TAB 2 : Analyse par commune
    with tab_par_commune:
        vue_commune = st.radio("Choisir la vue :", ["NICAD par commune", "Délibération par commune"])
        if vue_commune == "NICAD par commune":
            commune_nicad_data = df_parcelles.groupby(["commune", "nicad"]).size().reset_index(name="Nombre de parcelles")
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
            commune_delib_data = df_parcelles.groupby(["commune", "statut_deliberation"]).size().reset_index(name="Nombre de parcelles")
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

    # TAB 3 : Analyse détaillée
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
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total parcelles", len(df_filtre))
        col2.metric("Parcelles NICAD", (df_filtre["nicad"] == "Avec NICAD").sum())
        col3.metric("Parcelles délibérées", (df_filtre["statut_deliberation"] == "Délibérée").sum())
        col4.metric("Superficie totale", f"{df_filtre['superficie'].sum():,.2f}")

    # TAB 4 : Données
    with tab_donnees:
        st.subheader("🧾 Données filtrées")
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
        df_filtre_final = df_parcelles[
            (df_parcelles["nicad"].isin(nicad_filter)) &
            (df_parcelles["statut_deliberation"].isin(delib_filter))
        ]
        colonnes_affichees = ["commune", "village", "nicad", "statut_deliberation", "superficie"]
        if "type_usag" in df_parcelles.columns:
            colonnes_affichees.append("type_usag")
        st.dataframe(df_filtre_final[colonnes_affichees], use_container_width=True)
