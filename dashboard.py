import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Chargement des données
@st.cache_data
def charger_parcelles():
    df = pd.read_excel("parcelles.xlsx", engine="openpyxl")
    df.columns = df.columns.str.lower()
    # Traitement du statut NICAD
    df["nicad"] = df["nicad"].astype(str).str.strip().str.lower() == "oui"
    df["nicad"] = df["nicad"].map({True: "Avec NICAD", False: "Sans NICAD"})

    # Ajout du traitement pour les parcelles délibérées
    # Si la colonne existe déjà, utiliser cette colonne, sinon créer une colonne par défaut
    if "deliberee" in df.columns:
        df["deliberee"] = df["deliberee"].astype(str).str.strip().str.lower() == "oui"
        df["statut_deliberation"] = df["deliberee"].map({True: "Délibérée", False: "Non délibérée"})
    else:
        # Colonne par défaut si elle n'existe pas dans le fichier
        df["statut_deliberation"] = "Non délibérée"

    # Conversion et nettoyage des données
    df["superficie"] = pd.to_numeric(df["superficie"], errors="coerce")
    df["village"] = df["village"].fillna("Non spécifié").replace("", "Non spécifié")
    df["commune"] = df["commune"].fillna("Non spécifié").replace("", "Non spécifié")
    return df


df_parcelles = charger_parcelles()

st.title("📊 Tableau de Bord PROCASEF - Boundou")

onglet = st.sidebar.radio("Choisissez une vue :", ["Répartition des parcelles", "État d'avancement"])

if onglet == "Répartition des parcelles":
    # ========================
    # Statistiques Globales
    # ========================
    with st.expander("📌 Statistiques Globales", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nombre total de parcelles", len(df_parcelles))
        col2.metric("Parcelles NICAD", (df_parcelles["nicad"] == "Avec NICAD").sum())
        col3.metric("Parcelles délibérées", (df_parcelles["statut_deliberation"] == "Délibérée").sum())
        col4.metric("Superficie totale (m²)", f"{df_parcelles['superficie'].sum():,.2f}")

    # ========================
    # Répartition NICAD globale
    # ========================
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

    # ========================
    # Relation entre NICAD et délibération
    # ========================
    with st.expander("🔄 Relation entre NICAD et délibération", expanded=True):
        nicad_delib_data = df_parcelles.groupby(["nicad", "statut_deliberation"]).size().reset_index(
            name="Nombre de parcelles")
        fig_relation = px.bar(nicad_delib_data, x="nicad", y="Nombre de parcelles", color="statut_deliberation",
                              barmode="group", title="Relation entre statut NICAD et délibération",
                              labels={"nicad": "Statut NICAD", "statut_deliberation": "Statut délibération"})
        st.plotly_chart(fig_relation, use_container_width=True, key="relation_bar")

    # ========================
    # Répartition par Usage
    # ========================
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
    # ========================
    # Statistiques par commune et village
    # ========================
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

    # ========================
    # Statistiques par commune (Bar chart)
    # ========================
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

    # ========================
    # Taux de délibération par commune
    # ========================
    with st.expander("📊 Taux de délibération par commune", expanded=True):
        # Correction pour éviter l'avertissement de dépréciation
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

    # ========================
    # Données filtrées
    # ========================
    with st.expander("🧾 Données filtrées", expanded=True):
        colonnes_affichees = ["commune", "village", "nicad", "statut_deliberation", "superficie"]
        if "type_usag" in df_filtre.columns:
            colonnes_affichees.append("type_usag")

        st.dataframe(df_filtre[colonnes_affichees], use_container_width=True)

elif onglet == "État d'avancement":
    st.header("📅 État d'avancement des communes")
    df_etapes = pd.read_excel("Etat des opérations Boundou-Mai 2025.xlsx", engine="openpyxl")
    df_etapes.fillna("", inplace=True)


    def evaluer_progres(etapes):
        # Correction: Considère une étape débutée même si elle n'est pas encore complétée
        total = 4  # 4 étapes clés
        score = 0
        etapes_list = [e.strip().lower() for e in etapes.split("\n") if e.strip() != ""]

        for etape in etapes_list:
            if "complét" in etape or "affichage public (complétés)" in etape:
                score += 1
            elif "en cours" in etape or "débuté" in etape or "commencé" in etape:
                score += 0.5  # Attribuer un demi-point pour les étapes en cours

        return (score / total) * 100


    df_etapes["Progrès (%)"] = df_etapes["Progrès des étapes"].apply(evaluer_progres)

    # Calculer le nombre de communes débutées (ayant un progrès > 0%)
    # Correction: Une commune est considérée comme débutée si elle a un score minimum
    communes_debutees = df_etapes[df_etapes["Progrès (%)"] > 0]
    pourcentage_debutees = (len(communes_debutees) / len(df_etapes)) * 100 if len(df_etapes) > 0 else 0

    # Afficher le nombre de communes débutées pour diagnostic
    st.sidebar.info(f"Nombre de communes débutées: {len(communes_debutees)}")

    regions = ["Toutes"] + sorted(df_etapes["Région"].dropna().unique())
    communes = ["Toutes"] + sorted(df_etapes["Commune"].dropna().unique())
    csigs = ["Tous"] + sorted(df_etapes["CSIG"].dropna().unique())

    region_sel = st.selectbox("🌍 Choisir une région :", regions)
    df_etapes_filtre = df_etapes if region_sel == "Toutes" else df_etapes[df_etapes["Région"] == region_sel]

    commune_sel = st.selectbox("🏘️ Choisir une commune :", ["Toutes"] + sorted(df_etapes_filtre["Commune"].unique()))
    df_etapes_filtre = df_etapes_filtre if commune_sel == "Toutes" else df_etapes_filtre[
        df_etapes_filtre["Commune"] == commune_sel]

    csig_sel = st.selectbox("📌 Choisir un CSIG :", ["Tous"] + sorted(df_etapes_filtre["CSIG"].unique()))
    df_etapes_filtre = df_etapes_filtre if csig_sel == "Tous" else df_etapes_filtre[
        df_etapes_filtre["CSIG"] == csig_sel]

    # Affichage d'une légende des couleurs
    st.write("""
    ## Légende des indicateurs d'avancement:
    """)

    col_leg1, col_leg2, col_leg3, col_leg4 = st.columns(4)
    with col_leg1:
        st.markdown("🔴 **0-25%** : Non commencé")
    with col_leg2:
        st.markdown("🟠 **25-50%** : En cours")
    with col_leg3:
        st.markdown("🟡 **50-75%** : En cours avancé")
    with col_leg4:
        st.markdown("🟢 **75-100%** : Près de la fin")

    st.markdown("---")

    # Si aucune sélection spécifique n'est faite (région, commune et CSIG sur "Toutes/Tous")
    if region_sel == "Toutes" and commune_sel == "Toutes" and csig_sel == "Tous":
        st.subheader("📊 Vue globale de l'avancement du projet")

        # Statistiques globales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nombre total de communes", len(df_etapes))
        with col2:
            st.metric("Communes ayant débuté", len(communes_debutees))
        with col3:
            st.metric("Pourcentage de démarrage", f"{pourcentage_debutees:.1f}%")

        # Pour diagnostic: Afficher les détails des communes débutées
        with st.expander("Détails des communes débutées (diagnostic)", expanded=False):
            st.dataframe(communes_debutees[["Commune", "Progrès (%)", "Progrès des étapes"]], use_container_width=True)

        # Graphique d'avancement global
        st.subheader("📈 Avancement moyen par région")

        # Calculer la moyenne de progression par région
        region_progress = df_etapes.groupby("Région")["Progrès (%)"].mean().reset_index()

        # Créer un graphique à barres pour les régions
        fig_regions_bar = px.bar(
            region_progress,
            x="Région",
            y="Progrès (%)",
            title="Progression moyenne par région",
            color="Progrès (%)",
            color_continuous_scale=["red", "orange", "gold", "green"],
            range_color=[0, 100]
        )

        fig_regions_bar.update_layout(
            height=400,
            xaxis_title="Région",
            yaxis_title="Progrès moyen (%)",
            yaxis=dict(range=[0, 100])
        )

        st.plotly_chart(fig_regions_bar, use_container_width=True)

        # Résumé des communes par état d'avancement
        st.subheader("🔍 Résumé des communes par état d'avancement")

        # Catégoriser les communes par leur état d'avancement
        df_etapes["Catégorie"] = pd.cut(
            df_etapes["Progrès (%)"],
            bins=[0, 0.1, 25, 50, 75, 100],
            labels=["Non débutées", "Débutées (<25%)", "En cours (25-50%)", "Avancées (50-75%)",
                    "Presque terminées (>75%)"]
        )

        resume = df_etapes["Catégorie"].value_counts().reset_index()
        resume.columns = ["État d'avancement", "Nombre de communes"]

        fig_resume = px.pie(
            resume,
            values="Nombre de communes",
            names="État d'avancement",
            title="Répartition des communes par état d'avancement",
            color="État d'avancement",
            color_discrete_map={
                "Non débutées": "lightgray",
                "Débutées (<25%)": "red",
                "En cours (25-50%)": "orange",
                "Avancées (50-75%)": "gold",
                "Presque terminées (>75%)": "green"
            }
        )

        st.plotly_chart(fig_resume, use_container_width=True)

    # Si une région est sélectionnée mais pas de commune ou CSIG spécifique
    elif region_sel != "Toutes" and commune_sel == "Toutes" and csig_sel == "Tous":
        st.subheader(f"📊 Vue d'ensemble pour la région: {region_sel}")

        # Statistiques pour la région
        communes_region = len(df_etapes_filtre)
        communes_debutees_region = len(df_etapes_filtre[df_etapes_filtre["Progrès (%)"] > 0])
        pourcentage_debutees_region = (communes_debutees_region / communes_region) * 100 if communes_region > 0 else 0
        progres_moyen_region = df_etapes_filtre["Progrès (%)"].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Communes dans la région", communes_region)
        with col2:
            st.metric("Communes ayant débuté", communes_debutees_region)
        with col3:
            st.metric("Progrès moyen", f"{progres_moyen_region:.1f}%")

        # Tableau récapitulatif des communes de la région
        st.subheader(f"🏘️ Résumé des communes de {region_sel}")

        # Créer un tableau synthétique des communes
        resume_communes = df_etapes_filtre[["Commune", "CSIG", "Progrès (%)", "Date Début"]].copy()


        # Ajouter une colonne pour l'indicateur visuel
        def get_progress_indicator(progress):
            if progress < 0.1:
                return "⚪ Non débuté"
            elif progress < 25:
                return "🔴 Débuté"
            elif progress < 50:
                return "🟠 En cours"
            elif progress < 75:
                return "🟡 Avancé"
            else:
                return "🟢 Près de la fin"


        resume_communes["État"] = resume_communes["Progrès (%)"].apply(get_progress_indicator)

        # Trier par progrès décroissant
        resume_communes = resume_communes.sort_values(by="Progrès (%)", ascending=False)

        st.dataframe(resume_communes, use_container_width=True)

        # Graphique à barres pour visualiser l'avancement des communes
        fig_communes = px.bar(
            resume_communes.sort_values(by="Progrès (%)", ascending=True),
            y="Commune",
            x="Progrès (%)",
            orientation="h",
            color="Progrès (%)",
            color_continuous_scale=["red", "orange", "gold", "green"],
            title=f"Avancement des communes de {region_sel}",
            range_color=[0, 100]
        )

        fig_communes.update_layout(
            height=max(400, len(resume_communes) * 30),  # Adapter la hauteur au nombre de communes
            xaxis=dict(range=[0, 100])
        )

        st.plotly_chart(fig_communes, use_container_width=True)

    # Si une commune spécifique ou un CSIG spécifique est sélectionné, afficher les détails
    else:
        # Parcourir et afficher les données de chaque commune filtrée
        for idx, row in df_etapes_filtre.iterrows():
            progress = row["Progrès (%)"]

            # Détermination des couleurs selon le niveau d'avancement
            if progress < 25:
                color = "red"
                steps = [{"range": [0, 25], "color": "lightgray"}]
                threshold_color = "red"
            elif progress < 50:
                color = "orange"
                steps = [{"range": [0, 25], "color": "red"}, {"range": [25, 50], "color": "lightgray"}]
                threshold_color = "orange"
            elif progress < 75:
                color = "gold"
                steps = [{"range": [0, 25], "color": "red"}, {"range": [25, 50], "color": "orange"},
                         {"range": [50, 75], "color": "lightgray"}]
                threshold_color = "gold"
            else:
                color = "green"
                steps = [{"range": [0, 25], "color": "red"}, {"range": [25, 50], "color": "orange"},
                         {"range": [50, 75], "color": "gold"}, {"range": [75, 100], "color": "lightgray"}]
                threshold_color = "green"

            st.subheader(f"Avancement pour {row['Commune']} - CSIG : {row['CSIG']}")

            # Créer deux colonnes pour afficher la jauge et les informations
            col1, col2 = st.columns([1, 2])

            with col1:
                # Création d'une jauge (gauge) stylisée
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=progress,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": f"Progrès: {progress:.1f}%"},
                    gauge={
                        "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkblue"},
                        "bar": {"color": color},
                        "bgcolor": "white",
                        "borderwidth": 2,
                        "bordercolor": "gray",
                        "steps": steps,
                        "threshold": {
                            "line": {"color": "black", "width": 4},
                            "thickness": 0.75,
                            "value": progress
                        }
                    }
                ))

                # Configuration du layout pour une meilleure visualisation
                fig.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=50, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font={"color": "darkblue", "family": "Arial"}
                )

                st.plotly_chart(fig, use_container_width=True, key=f"gauge_{row['Commune']}_{idx}")

            with col2:
                # Affichage des informations de la commune
                start_date = row.get("Date Début", "Non spécifiée")
                expected_end_date = row.get("Date de prévision de compléter les inventaires fonciers", "Non spécifiée")

                st.write(f"📅 **Date de début des opérations** : {start_date}")
                st.write(f"📅 **Date de fin prévue** : {expected_end_date}")

                # Affichage des étapes d'avancement sous forme de tableau
                etapes = row.get("Progrès des étapes", "").split("\n")

                st.write("#### 🔄 Progression des étapes:")

                # Création d'un tableau d'avancement avec des indicateurs colorés
                etapes_data = [
                    ["1. Levés topo et enquêtes", etapes[0] if len(etapes) > 0 else "Non spécifié"],
                    ["2. Affichage public", etapes[1] if len(etapes) > 1 else "Non spécifié"],
                    ["3. Réunion du CTASF", etapes[2] if len(etapes) > 2 else "Non spécifié"],
                    ["4. Délibération", etapes[3] if len(etapes) > 3 else "Non spécifié"]
                ]

                for etape in etapes_data:
                    status = etape[1].lower()
                    if "complét" in status:
                        icon = "✅"
                    elif "en cours" in status:
                        icon = "🔄"
                    else:
                        icon = "⭕"

                    st.write(f"{icon} **{etape[0]}** : {etape[1]}")

            # Ligne de séparation entre les communes
            st.markdown("---")

        # Si aucune commune n'est trouvée après filtrage
        if len(df_etapes_filtre) == 0:
            st.warning("Aucune commune ne correspond aux critères de filtrage sélectionnés.")
