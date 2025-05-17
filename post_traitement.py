# post_traitement.py

import streamlit as st
from streamlit_lottie import st_lottie
import requests

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def afficher_post_traitement(df=None):
    lottie_construction = load_lottie_url("https://lottie.host/34c3adf6-1799-486f-aec5-70ce5393fe8c/b2XRRd3cfh.json")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st_lottie(
            lottie_construction,
            speed=1,
            reverse=False,
            loop=True,
            quality="high",
            height=300
        )

        st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h1 style='font-size: 2.5em; color: #f39c12;'>🚧 Page en construction</h1>
                <p style='font-size: 1.3em; color: #444;'>
                    Cette section dédiée au post-traitement des parcelles sera bientôt disponible.
                </p>
                <p style='font-size: 1.1em; color: #777;'>Merci de votre patience 🙏</p>
            </div>
        """, unsafe_allow_html=True)
