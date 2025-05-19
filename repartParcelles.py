import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def afficher_repartition(df_parcelles):
    """
    Affiche l'onglet de répartition des parcelles avec des onglets (tabs)
    """

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📌 Statistiques Globales",
        "📊 NICAD & Délibérations",
        "🏗️ Répartition par usage",
        "📍 Commune & Village",
        "🏘️ Répartition par commune",
        "📈 Taux de délibération",
        "🧾 Données filtrées"
    ])

    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nombre total de parcelles", len(df_parcelles))
        col2.metric("Parcelles NICAD", (df_parcelles["nicad"] == "Avec NICAD").sum())
        col3.metric("Parcelles délibérées (🔄)", (df_parcelles["statut_deliberation"] == "Délibérée").sum())
        col4.metric("Superficie totale (m²)", f"{df_parcelles['superficie'].sum():,.2f}")

    with tab2:
        afficher_repartition_nicad_globale(df_parcelles)
        afficher_relation_nicad_deliberation(df_parcelles)

    with tab3:
        afficher_repartition_par_usage(df_parcelles)

    with tab4:
        afficher_stats_commune_village(df_parcelles)

    with tab5:
        afficher_repartition_par_commune(df_parcelles)

    with tab6:
        afficher_taux_deliberation_commune(df_parcelles)

    with tab7:
        colonnes_affichees = ["commune", "village", "nicad", "statut_deliberation", "superficie"]
        if "type_usag" in df_parcelles.columns:
            colonnes_affichees.append("type_usag")
        st.dataframe(df_parcelles[colonnes_affichees], use_container_width=True)


def afficher_repartition_nicad_globale(df_parcelles):
    """Affiche la répartition globale des parcelles NICAD"""
    with st.expander("📊 Répartition globale des parcelles NICAD", expanded=True):
        # Option pour afficher/cacher les graphiques
        display_option = st.radio("Afficher les graphiques :",
                                  ["Les deux", "NICAD uniquement", "Délibération uniquement"])

        # Affichage des graphiques dans une seule colonne
        if display_option in ["Les deux", "NICAD uniquement"]:
            fig_global_nicad = px.pie(df_parcelles, names="nicad", title="Répartition globale des parcelles NICAD",
                                      labels={"nicad": "Statut NICAD"})
            st.plotly_chart(fig_global_nicad, use_container_width=True, key="global_nicad_pie")

        if display_option in ["Les deux", "Délibération uniquement"]:
            fig_global_deliberation = px.pie(df_parcelles, names="statut_deliberation",
                                             title="Répartition des parcelles délibérées",
                                             labels={"statut_deliberation": "Statut délibération"})
            st.plotly_chart(fig_global_deliberation, use_container_width=True, key="global_deliberation_pie")


def afficher_relation_nicad_deliberation(df_parcelles):
    """Affiche la relation entre NICAD et délibération"""
    with st.expander("🔄 Relation entre NICAD et délibération", expanded=True):
        nicad_delib_data = df_parcelles.groupby(["nicad", "statut_deliberation"]).size().reset_index(
            name="Nombre de parcelles")
        fig_relation = px.bar(nicad_delib_data, x="nicad", y="Nombre de parcelles", color="statut_deliberation",
                              barmode="group", title="Relation entre statut NICAD et délibération",
                              labels={"nicad": "Statut NICAD", "statut_deliberation": "Statut délibération"})
        st.plotly_chart(fig_relation, use_container_width=True, key="relation_bar")


def afficher_repartition_par_usage(df_parcelles):
    """Affiche la répartition par usage des parcelles"""
    with st.expander("🏗️ Répartition par usage des parcelles", expanded=True):
        if "type_usag" in df_parcelles.columns:
            # Option pour afficher/cacher les graphiques
            display_option_usage = st.radio("Afficher les graphiques :",
                                            ["Les deux", "Usage uniquement", "Délibération uniquement"])

            # Affichage des graphiques dans une seule colonne
            if display_option_usage in ["Les deux", "Usage uniquement"]:
                fig_usage = px.pie(df_parcelles, names="type_usag", title="Répartition des usages",
                                   labels={"type_usag": "Usage"})
                st.plotly_chart(fig_usage, use_container_width=True, key="usage_pie")

            if display_option_usage in ["Les deux", "Délibération uniquement"]:
                # Graphique montrant la répartition des délibérations par type d'usage
                usage_delib_data = df_parcelles.groupby(["type_usag", "statut_deliberation"]).size().reset_index(
                    name="Nombre")
                fig_usage_delib = px.bar(usage_delib_data, x="type_usag", y="Nombre", color="statut_deliberation",
                                         barmode="group", title="Délibération par type d'usage",
                                         labels={"type_usag": "Usage", "statut_deliberation": "Statut délibération"})
                st.plotly_chart(fig_usage_delib, use_container_width=True, key="usage_delib_bar")
        else:
            st.info("Aucune colonne 'type_usag' trouvée dans les données.")


def afficher_stats_commune_village(df_parcelles):
    """Affiche les statistiques par commune et village"""
    with st.expander("📍 Statistiques par commune et village", expanded=True):
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

        st.subheader(f"📍 Statistiques pour : {village_selectionne} ({commune_selectionnee})")
        col4, col5, col6, col7 = st.columns(4)
        col4.metric("Total parcelles", len(df_filtre))
        col5.metric("Parcelles NICAD", (df_filtre["nicad"] == "Avec NICAD").sum())
        col6.metric("Parcelles délibérées", (df_filtre["statut_deliberation"] == "Délibérée").sum())
        col7.metric("Superficie totale", f"{df_filtre['superficie'].sum():,.2f}")

        # Option pour afficher/cacher les graphiques
        display_village_option = st.radio("Afficher les graphiques pour ce village/commune :",
                                          ["Les deux", "NICAD uniquement", "Délibération uniquement"],
                                          key="village_display_option")

        # Affichage des graphiques dans un ordre séquentiel
        if display_village_option in ["Les deux", "NICAD uniquement"]:
            st.subheader("📊 Répartition des parcelles NICAD")
            fig_village_nicad = px.pie(df_filtre, names="nicad", title="Répartition NICAD - Données filtrées",
                                       labels={"nicad": "NICAD"})
            st.plotly_chart(fig_village_nicad, use_container_width=True, key="village_nicad_pie")

        if display_village_option in ["Les deux", "Délibération uniquement"]:
            st.subheader("📊 Répartition des parcelles délibérées")
            fig_village_delib = px.pie(df_filtre, names="statut_deliberation",
                                       title="Répartition délibération - Données filtrées",
                                       labels={"statut_deliberation": "Délibération"})
            st.plotly_chart(fig_village_delib, use_container_width=True, key="village_delib_pie")


def afficher_repartition_par_commune(df_parcelles):
    """Affiche la répartition des parcelles par commune"""
    with st.expander("🏘️ Répartition des parcelles par commune", expanded=True):
        # Onglets pour choisir entre la vue NICAD et la vue délibération
        vue_commune = st.radio("Choisir la vue :", ["NICAD par commune", "Délibération par commune"])

        if vue_commune == "NICAD par commune":
            commune_nicad_data = df_parcelles.groupby(["commune", "nicad"]).size().reset_index(
                name="Nombre de parcelles")
            fig_commune_nicad = px.bar(commune_nicad_data, x="commune", y="Nombre de parcelles", color="nicad",
                                       barmode="group", title="Parcelles avec/sans NICAD par commune",
                                       labels={"nicad": "NICAD"})
            st.plotly_chart(fig_commune_nicad, use_container_width=True, key="commune_nicad_bar")
        else:
            commune_delib_data = df_parcelles.groupby(["commune", "statut_deliberation"]).size().reset_index(
                name="Nombre de parcelles")
            fig_commune_delib = px.bar(commune_delib_data, x="commune", y="Nombre de parcelles",
                                       color="statut_deliberation",
                                       barmode="group", title="Parcelles délibérées/non délibérées par commune",
                                       labels={"statut_deliberation": "Statut délibération"})
            st.plotly_chart(fig_commune_delib, use_container_width=True, key="commune_delib_bar")


def afficher_taux_deliberation_commune(df_parcelles):
    """Affiche le taux de délibération par commune"""
    with st.expander("📊 Taux de délibération par commune", expanded=True):
        # Calculer le taux de délibération par commune sans utiliser apply
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

        fig_taux_delib = px.bar(taux_delib, x="commune", y="Taux de délibération (%)",
                                title="Taux de délibération par commune (%)",
                                color="Taux de délibération (%)",
                                color_continuous_scale=["red", "orange", "green"],
                                labels={"commune": "Commune"})

        st.plotly_chart(fig_taux_delib, use_container_width=True, key="taux_delib_bar")
