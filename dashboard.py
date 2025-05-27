import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# Configuration de la page - DOIT ÊTRE EN PREMIER
st.set_page_config(
    page_title="PROCASEF - Boundou",
    page_icon="logo/BETPLUAUDETAG.jpg",  # Icône de l'onglet
    layout="wide"
)

# Imports des modules internes
import repartParcelles
import progression
from projections_2025 import afficher_projections_2025
import genre_dashboard
import post_traitement
from data_loader import (
    charger_parcelles, 
    charger_levee_par_commune, 
    charger_parcelles_terrain_periode, 
    charger_etapes
)

def main():
    # --- SIDEBAR ---
    with st.sidebar:
        # Personnalisation du fond de la sidebar (facultatif)
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

        # Insertion du logo animé (GIF)
        st.markdown(
            """
            <div style='text-align: center;'>
                <img src='logo/BETPLUAUDETAG.gif' width='120'>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Titre et description
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

        # Menu de navigation
        selected = option_menu(
            menu_title=None,
            options=[
                "Répartition des parcelles",
                "État d'avancement",
                "Projections 2025",
                "Répartition du genre",
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

    # --- CONTENU PRINCIPAL ---
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

    elif selected == "Post-traitement":
        post_traitement.afficher_analyse_parcelles()

if __name__ == "__main__":
    main()
