import json
import streamlit as st
from streamlit_lottie import st_lottie

def load_lottie_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def afficher_post_traitement(df=None):
    try:
        lottie_construction = load_lottie_file("lottie/Animation - 1747510433900.json")
    except Exception as e:
        st.error(f"Erreur chargement animation : {e}")
        lottie_construction = None

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if lottie_construction:
            st_lottie(
                lottie_construction,
                speed=1,
                loop=True,
                quality="high",
                height=300,
            )
        else:
            st.warning("⚠️ Animation indisponible")

        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1 style="color: #f39c12;">🚧 Page en construction</h1>
                <p style="color: #444; font-size: 1.3em;">Cette section sera bientôt disponible.</p>
                <p style="color: #777;">Merci de votre patience 🙏</p>
            </div>
        """, unsafe_allow_html=True)
