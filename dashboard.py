import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import base64

# Configuration de la page - DOIT ÊTRE EN PREMIER
st.set_page_config(
    page_title="PROCASEF - Boundou",
    page_icon="logo/BETPLUSAUDETAG.jpg",  # Icône de l'onglet
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
    charger_etapes,
    interface_telechargement_fichier
)

# --- FONCTIONS UTILES ---
def load_gif_as_base64(gif_path):
    """Charge un GIF et le convertit en base64 pour l'affichage dans Streamlit"""
    try:
        with open(gif_path, "rb") as f:
            contents = f.read()
        return base64.b64encode(contents).decode("utf-8")
    except FileNotFoundError:
        return None


# --- APPLICATION PRINCIPALE ---
def main():
    # --- SIDEBAR ---
    with st.sidebar:
        # Personnalisation du fond de la sidebar
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

        # Insertion du GIF animé ou fallback
        gif_base64 = load_gif_as_base64("logo/BETPLUAUDETAG_SMALL.gif")

        if gif_base64:
            st.markdown(
                f"""
                <div style='display: flex; justify-content: center; margin: 0 auto; padding: 0;'>
                    <img src='data:image/gif;base64,{gif_base64}' 
                         style='width: 100px; height: auto; border-radius: 8px; display: block; margin: 0; padding: 0; box-shadow: none; background: transparent;'>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style='text-align: center; margin-bottom: 20px;'>
                    <div style='width: 120px; height: 80px; background-color: #f39c12; border-radius: 10px; 
                                display: flex; align-items: center; justify-content: center; margin: 0 auto;'>
                        <span style='color: white; font-size: 18px; font-weight: bold;'>LOGO</span>
                    </div>
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

    # Chargement des données avec gestion des erreurs
    df_parcelles = charger_parcelles()
    
    # Vérifier si les données sont présentes
    if df_parcelles.empty:
        # Vérifier si on a des données uploadées dans la session
        if 'df_parcelles_uploaded' in st.session_state:
            df_parcelles = st.session_state['df_parcelles_uploaded']
        else:
            # Afficher l'interface de téléchargement
            df_uploaded = interface_telechargement_fichier()
            if not df_uploaded.empty:
                df_parcelles = df_uploaded
            else:
                # Afficher un message d'information et arrêter l'exécution
                st.info("🔄 Veuillez télécharger un fichier de données pour commencer l'analyse.")
                return

    # Maintenant procéder avec l'affichage des différents modules
    if selected == "Répartition des parcelles":
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


# --- POINT D'ENTRÉE ---
if __name__ == "__main__":
    main()
