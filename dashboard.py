import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# Modules internes
import repartParcelles
import progression
from projections_2025 import afficher_projections_2025
import genre_dashboard
import post_traitement

# Configuration de la page
st.set_page_config(
    page_title="PROCASEF - Boundou",
    page_icon="logo/BETPLUSAUDETAG.jpg",
    layout="wide"
)

# Cache des données
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
def charger_levee_par_commune():
    df = pd.read_excel("data/Levee par commune Terrain_URM.xlsx", engine="openpyxl")
    df.fillna("", inplace=True)
    return df


@st.cache_data
def charger_parcelles_terrain_periode():
    df = pd.read_excel("data/Parcelles_terrain_periode.xlsx", engine="openpyxl")
    df.columns = df.columns.str.lower()
    df["superficie"] = pd.to_numeric(df["superficie"], errors="coerce")
    df["commune"] = df["commune"].fillna("Non spécifié").replace("", "Non spécifié")
    df["periode"] = df["periode"].fillna("Non spécifié").replace("", "Non spécifié")
    return df


@st.cache_data
def charger_etapes():
    df = pd.read_excel("data/Etat des opérations Boundou-Mai 2025.xlsx", engine="openpyxl")
    df.fillna("", inplace=True)
    return df


def main():
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(
            """
            <style>
            .sidebar .sidebar-content {
                background-color: #001f3f;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.image("logo/BETPLUSAUDETAG.jpg", width=120)

        st.markdown(
            """
            <div style='text-align:center;'>
                <h2 style='color:#f39c12;'>PROCASEF Boundou</h2>
                <p style='color:#ffffff; font-size:14px;'>Tableau de bord interactif</p>
                <hr style='border:1px solid #f39c12;'>
            </div>
            """,
            unsafe_allow_html=True
        )

        selected = option_menu(
            menu_title=None,
            options=[
                "Répartition des parcelles",
                "État d'avancement",
                "Projections 2025",
                "Répartition du genre",
                "Analyse des parcelles",  # ✔️ Conservé
                "Post-traitement"
            ],
            icons=["map", "bar-chart-line", "calendar", "gender-female", "search", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "#001f3f"},
                "icon": {"color": "#f39c12", "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "color": "#ffffff",
                    "--hover-color": "#f39c12",
                },
                "nav-link-selected": {
                    "background-color": "#f39c12",
                    "color": "white"
                },
            }
        )

    # --- CONTENU ---
    st.title("📊 Tableau de Bord PROCASEF - Boundou")

    if selected == "Répartition des parcelles":
        df_parcelles = charger_parcelles()
        repartParcelles.afficher_dashboard_parcelles(df_parcelles)

    elif selected == "État d'avancement":
        df_etapes = charger_etapes()
        progression.afficher_etat_avancement(df_etapes)

    elif selected == "Projections 2025":
        afficher_projections_2025()

    elif selected == "Répartition du genre":
        genre_dashboard.afficher_repartition_genre()
        
    elif selected == "Analyse des parcelles":  # ✔️ Utilise maintenant post_traitement
        post_traitement.afficher_analyse_parcelles()

    elif selected == "Post-traitement":
        post_traitement.afficher_analyse_parcelles()  # Ou une autre fonction si différente

if __name__ == "__main__":
    main()
