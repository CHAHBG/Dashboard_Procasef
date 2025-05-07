import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def afficher_etat_avancement(df_etapes=None):
    """
    Fonction principale pour afficher l'onglet État d'avancement des communes

    Args:
        df_etapes: DataFrame optionnel contenant les données d'avancement.
                  Si None, les données seront chargées depuis le fichier Excel.
    """
    st.header("📅 État d'avancement des communes")

    # Chargement des données si non fournies
    if df_etapes is None:
        df_etapes = charger_donnees_etapes()
    else:
        # S'assurer que les calculs de progrès sont effectués sur les données fournies
        if "Progrès (%)" not in df_etapes.columns:
            df_etapes["Progrès (%)"] = df_etapes["Progrès des étapes"].apply(evaluer_progres)

    # Interface de filtrage
    region_sel, commune_sel, csig_sel, df_etapes_filtre = filtrer_donnees(df_etapes)

    # Afficher la légende
    afficher_legende()

    # Afficher le contenu approprié selon les filtres
    if region_sel == "Toutes" and commune_sel == "Toutes" and csig_sel == "Tous":
        afficher_vue_globale(df_etapes)
    elif region_sel != "Toutes" and commune_sel == "Toutes" and csig_sel == "Tous":
        afficher_vue_region(df_etapes_filtre, region_sel)
    else:
        afficher_details_communes(df_etapes_filtre)


@st.cache_data
def charger_donnees_etapes():
    """
    Charge et prépare les données d'état d'avancement
    """
    df_etapes = pd.read_excel("data/Etat des opérations Boundou-Mai 2025.xlsx", engine="openpyxl")
    df_etapes.fillna("", inplace=True)

    # Calcul du progrès en pourcentage
    df_etapes["Progrès (%)"] = df_etapes["Progrès des étapes"].apply(evaluer_progres)

    return df_etapes


def evaluer_progres(etapes):
    """
    Évalue le progrès d'une commune basé sur les étapes décrites
    """
    # Considère une étape débutée même si elle n'est pas encore complétée
    total = 4  # 4 étapes clés
    score = 0
    etapes_list = [e.strip().lower() for e in etapes.split("\n") if e.strip() != ""]

    for etape in etapes_list:
        if "complét" in etape or "affichage public (complétés)" in etape:
            score += 1
        elif "en cours" in etape or "débuté" in etape or "commencé" in etape:
            score += 0.5  # Attribuer un demi-point pour les étapes en cours

    return (score / total) * 100


def filtrer_donnees(df_etapes):
    """
    Filtre les données selon les sélections de l'utilisateur
    """
    regions = ["Toutes"] + sorted(df_etapes["Région"].dropna().unique())
    region_sel = st.selectbox("🌍 Choisir une région :", regions)
    df_etapes_filtre = df_etapes if region_sel == "Toutes" else df_etapes[df_etapes["Région"] == region_sel]

    commune_sel = st.selectbox("🏘️ Choisir une commune :",
                               ["Toutes"] + sorted(df_etapes_filtre["Commune"].unique()))
    df_etapes_filtre = df_etapes_filtre if commune_sel == "Toutes" else df_etapes_filtre[
        df_etapes_filtre["Commune"] == commune_sel]

    csig_sel = st.selectbox("📌 Choisir un CSIG :",
                            ["Tous"] + sorted(df_etapes_filtre["CSIG"].unique()))
    df_etapes_filtre = df_etapes_filtre if csig_sel == "Tous" else df_etapes_filtre[
        df_etapes_filtre["CSIG"] == csig_sel]

    return region_sel, commune_sel, csig_sel, df_etapes_filtre


def afficher_legende():
    """
    Affiche la légende des indicateurs d'avancement
    """
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


def afficher_vue_globale(df_etapes):
    """
    Affiche la vue globale de l'avancement du projet
    """
    st.subheader("📊 Vue globale de l'avancement du projet")

    # Calculer le nombre de communes débutées
    communes_debutees = df_etapes[df_etapes["Progrès (%)"] > 0]
    pourcentage_debutees = (len(communes_debutees) / len(df_etapes)) * 100 if len(df_etapes) > 0 else 0

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
        st.dataframe(communes_debutees[["Commune", "Progrès (%)", "Progrès des étapes"]],
                     use_container_width=True)

    # Graphique d'avancement par région
    afficher_avancement_regions(df_etapes)

    # Résumé des communes par état d'avancement
    afficher_resume_etat_avancement(df_etapes)


def afficher_avancement_regions(df_etapes):
    """
    Affiche le graphique d'avancement moyen par région
    """
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


def afficher_resume_etat_avancement(df_etapes):
    """
    Affiche le résumé des communes par état d'avancement
    """
    st.subheader("🔍 Résumé des communes par état d'avancement")

    # Catégoriser les communes par leur état d'avancement
    df_etapes["Catégorie"] = pd.cut(
        df_etapes["Progrès (%)"],
        bins=[0, 0.1, 25, 50, 75, 100],
        labels=["Non débutées", "Débutées (<25%)", "En cours (25-50%)",
                "Avancées (50-75%)", "Presque terminées (>75%)"]
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


def afficher_vue_region(df_etapes_filtre, region_sel):
    """
    Affiche la vue d'ensemble pour une région spécifique
    """
    st.subheader(f"📊 Vue d'ensemble pour la région: {region_sel}")

    # Statistiques pour la région
    communes_region = len(df_etapes_filtre)
    communes_debutees_region = len(df_etapes_filtre[df_etapes_filtre["Progrès (%)"] > 0])
    progres_moyen_region = df_etapes_filtre["Progrès (%)"].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Communes dans la région", communes_region)
    with col2:
        st.metric("Communes ayant débuté", communes_debutees_region)
    with col3:
        st.metric("Progrès moyen", f"{progres_moyen_region:.1f}%")

    # Tableau récapitulatif des communes de la région
    afficher_tableau_communes_region(df_etapes_filtre, region_sel)


def afficher_tableau_communes_region(df_etapes_filtre, region_sel):
    """
    Affiche le tableau récapitulatif des communes d'une région
    """
    st.subheader(f"🏘️ Résumé des communes de {region_sel}")

    # Créer un tableau synthétique des communes
    resume_communes = df_etapes_filtre[["Commune", "CSIG", "Progrès (%)", "Date Début"]].copy()

    # Ajouter une colonne pour l'indicateur visuel
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


def get_progress_indicator(progress):
    """
    Retourne l'indicateur visuel selon le niveau de progrès
    """
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


def afficher_details_communes(df_etapes_filtre):
    """
    Affiche les détails pour chaque commune filtrée
    """
    # Si aucune commune trouvée après filtrage
    if len(df_etapes_filtre) == 0:
        st.warning("Aucune commune ne correspond aux critères de filtrage sélectionnés.")
        return

    # Parcourir et afficher les données de chaque commune filtrée
    for idx, row in df_etapes_filtre.iterrows():
        progress = row["Progrès (%)"]

        # Détermination des couleurs selon le niveau d'avancement
        color, steps, threshold_color = determiner_parametres_jauge(progress)

        st.subheader(f"Avancement pour {row['Commune']} - CSIG : {row['CSIG']}")

        # Créer deux colonnes pour afficher la jauge et les informations
        col1, col2 = st.columns([1, 2])

        with col1:
            afficher_jauge_progres(progress, color, steps)

        with col2:
            afficher_infos_commune(row)

        # Ligne de séparation entre les communes
        st.markdown("---")


def determiner_parametres_jauge(progress):
    """
    Détermine les paramètres de couleur pour la jauge de progrès
    """
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

    return color, steps, threshold_color


def afficher_jauge_progres(progress, color, steps):
    """
    Affiche une jauge de progrès pour une commune
    """
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

    st.plotly_chart(fig, use_container_width=True)


def afficher_infos_commune(row):
    """
    Affiche les informations détaillées d'une commune
    """
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


# Alias pour compatibilité
def afficher_progression(df_etapes=None):
    """
    Fonction de compatibilité pour l'appel depuis dashboard.py
    Cette fonction est un simple alias vers afficher_etat_avancement

    Args:
        df_etapes: DataFrame optionnel contenant les données d'avancement
    """
    afficher_etat_avancement(df_etapes)


if __name__ == "__main__":
    # Ce code s'exécute uniquement si le fichier est exécuté directement
    # Utile pour les tests
    st.set_page_config(
        page_title="PROCASEF - État d'avancement",
        page_icon="📊",
        layout="wide"
    )
    afficher_etat_avancement()