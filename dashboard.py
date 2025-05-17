import streamlit as st
import pandas as pd

# Config de page
st.set_page_config(
    page_title="PROCASEF - Boundou",
    page_icon="logo/BETPLUSAUDETAG.jpg",
    layout="wide"
)

# Imports modules internes
import repartParcelles
import progression
from projections_2025 import afficher_projections_2025
import genre_dashboard
import post_traitement

# Chargement des données
@st.cache_data
def charger_parcelles():
    df = pd.read_excel("data/parcelles.xlsx", engine="openpyxl")
    df.columns = df.columns.str.lower()
    df["nicad"] = df["nicad"].astype(str).str.strip().str.lower() == "oui"
    df["nicad"] = df["nicad"].map({True: "Avec NICAD", False: "Sans NICAD"})

    if "deliberee" in df.columns:
        df["deliberee"] = df["deliberee"].astype(str).str.strip().str.lower() == "oui"
        df["statut_deliberation"] = df["deliberee"].map({True: "Délibérée", False: "Non délibérée"})
    else:
        df["statut_deliberation"] = "Non délibérée"

    df["superficie"] = pd.to_numeric(df["superficie"], errors="coerce")
    df["village"] = df["village"].fillna("Non spécifié").replace("", "Non spécifié")
    df["commune"] = df["commune"].fillna("Non spécifié").replace("", "Non spécifié")
    return df

@st.cache_data
def charger_etapes():
    df = pd.read_excel("data/Etat des opérations Boundou-Mai 2025.xlsx", engine="openpyxl")
    df.fillna("", inplace=True)
    return df

@st.cache_data
def charger_post_traitement():
    try:
        df = pd.read_excel("data/parcelles_topos_post_traitement.xlsx", engine="openpyxl")
        df.fillna("", inplace=True)
        df.columns = df.columns.str.lower()
        return df
    except:
        return pd.DataFrame()  # temporaire si fichier non prêt

# Application principale
def main():
    st.title("📊 Tableau de Bord PROCASEF - Boundou")

    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <img src="https://raw.githubusercontent.com/tonlogo/BETPLUSAUDETAG.jpg" alt="Logo" style="width: 100px; border-radius: 10px;"/>
        <h2 style="margin-top: 0.5rem; color: #f39c12;">PROCASEF Boundou</h2>
        <p style="font-size: 0.9rem; color: #888;">Tableau de bord interactif</p>
        <hr style="border: 1px solid #f39c12;">
    </div>
    """, unsafe_allow_html=True)

    options = {
        "📍 Répartition des parcelles": "Répartition des parcelles",
        "📈 État d'avancement": "État d'avancement",
        "📅 Projections 2025": "Projections 2025",
        "⚧ Répartition du genre": "Répartition du genre",
        "⚙️ Post-traitement": "Post-traitement"
    }

    choix = st.sidebar.radio(
        "Navigation",
        options.keys(),
        index=0,
        label_visibility="visible"
    )
    onglet = options[choix]

    # Chargement et affichage selon onglet
    if onglet == "Répartition des parcelles":
        df_parcelles = charger_parcelles()
        repartParcelles.afficher_repartition(df_parcelles)
    elif onglet == "État d'avancement":
        df_etapes = charger_etapes()
        progression.afficher_etat_avancement(df_etapes)
    elif onglet == "Projections 2025":
        afficher_projections_2025()
    elif onglet == "Répartition du genre":
        genre_dashboard.afficher_repartition_genre()
    elif onglet == "Post-traitement":
        df_post = charger_post_traitement()
        post_traitement.afficher_post_traitement(df_post)


if __name__ == "__main__":
    main()
