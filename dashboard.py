import streamlit as st
import pandas as pd

# Configuration de la page – À placer absolument en premier après les imports
st.set_page_config(
    page_title="PROCASEF - Boundou",
    page_icon="logo/BETPLUSAUDETAG.jpg",  # ✅ Slashs compatibles Windows/Linux
    layout="wide"
)

# Imports internes (après la config Streamlit)
import repartParcelles
import progression
from projections_2025 import afficher_projections_2025
import genre_dashboard  # Ajout de l'import du nouveau module

# Chargement des données des parcelles
@st.cache_data
def charger_parcelles():
    df = pd.read_excel("parcelles.xlsx", engine="openpyxl")
    df.columns = df.columns.str.lower()

    # Traitement du statut NICAD
    df["nicad"] = df["nicad"].astype(str).str.strip().str.lower() == "oui"
    df["nicad"] = df["nicad"].map({True: "Avec NICAD", False: "Sans NICAD"})

    # Traitement des parcelles délibérées
    if "deliberee" in df.columns:
        df["deliberee"] = df["deliberee"].astype(str).str.strip().str.lower() == "oui"
        df["statut_deliberation"] = df["deliberee"].map({True: "Délibérée", False: "Non délibérée"})
    else:
        df["statut_deliberation"] = "Non délibérée"

    df["superficie"] = pd.to_numeric(df["superficie"], errors="coerce")
    df["village"] = df["village"].fillna("Non spécifié").replace("", "Non spécifié")
    df["commune"] = df["commune"].fillna("Non spécifié").replace("", "Non spécifié")
    return df

# Chargement des données d'étapes
@st.cache_data
def charger_etapes():
    df = pd.read_excel("data/Etat des opérations Boundou-Mai 2025.xlsx", engine="openpyxl")
    df.fillna("", inplace=True)
    return df

# Fonction principale
def main():
    st.title("📊 Tableau de Bord PROCASEF - Boundou")

    # Chargement des données
    df_parcelles = charger_parcelles()
    df_etapes = charger_etapes()

    # Onglets
    onglet = st.sidebar.radio(
        "Choisissez une vue :",
        [
            "Répartition des parcelles",
            "État d'avancement",
            "Projections 2025",
            "Répartition du genre"
        ]
    )

    if onglet == "Répartition des parcelles":
        repartParcelles.afficher_repartition(df_parcelles)
    elif onglet == "État d'avancement":
        progression.afficher_etat_avancement(df_etapes)
    elif onglet == "Projections 2025":
        afficher_projections_2025()
    elif onglet == "Répartition du genre":
        genre_dashboard.afficher_repartition_genre()

if __name__ == "__main__":
    main()