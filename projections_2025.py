import streamlit as st

# Configuration de la page - DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT
st.set_page_config(
    page_title="Suivi des Inventaires 2025",
    page_icon="📊",
    layout="wide"
)

import pandas as pd
import altair as alt
import time
import numpy as np

# Ajout des styles pour l'animation de vague
st.markdown("""
<style>
.wave-container {
    position: relative;
    width: 100%;
    height: 120px;
    overflow: hidden;
    border-radius: 10px;
    margin-bottom: 20px;
    background: #f0f2f6;
}

.wave {
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(to bottom, rgba(76, 175, 80, 0.7), rgba(76, 175, 80, 0.3));
    border-radius: 0 0 50% 50%;
    animation: wave 2s infinite linear;
}

.wave:nth-child(2) {
    animation-delay: 0.5s;
    opacity: 0.5;
}

.wave:nth-child(3) {
    animation-delay: 1s;
    opacity: 0.3;
}

.wave-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #000;
    font-size: 24px;
    font-weight: bold;
    z-index: 10;
}

@keyframes wave {
    0% {
        transform: translateY(100%) scale(1, 0.2);
    }
    50% {
        transform: translateY(60%) scale(1, 0.5);
    }
    100% {
        transform: translateY(100%) scale(1, 0.2);
    }
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def charger_projections():
    df = pd.read_excel("projections/Projections 2025.xlsx", engine="openpyxl")
    # Nettoyage des noms de colonnes
    df.columns = df.columns.str.strip().str.lower()
    return df

def wave_animation(value, max_value, text):
    """Crée une animation de vague avec la valeur affichée"""
    # Calculer la hauteur de remplissage en fonction du pourcentage
    percentage = min(value / max_value * 100, 100) if max_value > 0 else 0
    fill_height = min(100, percentage)  # Ne pas dépasser 100%
    
    wave_html = f"""
    <div class="wave-container">
        <div class="wave" style="bottom: {100-fill_height}%;"></div>
        <div class="wave" style="bottom: {100-fill_height}%;"></div>
        <div class="wave" style="bottom: {100-fill_height}%;"></div>
        <div class="wave-text">{text}</div>
    </div>
    """
    return wave_html

def afficher_projections_2025():
    st.header("📅 Projections des Inventaires - 2025")
    df = charger_projections()
    
    # Tentative intelligente de renommage automatique
    colonnes_cibles = {
        "mois": "mois",
        "inventaires mensuels réalisés": "realises",
        "réalisés": "realises",
        "objectif inventaires mensuels": "objectif_mensuel",
        "objectif mensuel": "objectif_mensuel",
        "objectif inventaires total": "objectif_total",
        "objectif total": "objectif_total",
    }
    
    colonnes_renommees = {}
    for col in df.columns:
        for cle in colonnes_cibles:
            if cle in col.lower():
                colonnes_renommees[col] = colonnes_cibles[cle]
                break
    
    df = df.rename(columns=colonnes_renommees)
    
    colonnes_obligatoires = ["mois", "realises", "objectif_mensuel", "objectif_total"]
    for col in colonnes_obligatoires:
        if col not in df.columns:
            st.error(f"❌ La colonne requise '{col}' est introuvable dans les données.")
            st.stop()
    
    df = df.dropna(subset=["mois"])
    df["realises"] = pd.to_numeric(df["realises"], errors="coerce").fillna(0)
    df["objectif_mensuel"] = pd.to_numeric(df["objectif_mensuel"], errors="coerce").fillna(0)
    df["objectif_total"] = pd.to_numeric(df["objectif_total"], errors="coerce").fillna(0)
    
    dernier_mois = df["mois"].iloc[-1]
    objectif_total = df["objectif_total"].iloc[-1]
    realises_total = 20558
    progression_pct = (realises_total / objectif_total) * 100 if objectif_total else 0
    # Animation de vague en haut de la page avec les métriques principales
    st.subheader("📌 Progression des levés réalisés")
    
    col1, col2, col3 = st.columns([2, 5, 2])
    
    # Affichage des métriques dans la première colonne
    col1.metric("Total réalisés", f"{realises_total:,}", f"{progression_pct:.1f} %")
    col1.metric("Objectif total", f"{objectif_total:,}")
    
    # Grande animation de vague au centre
    wave_container_css = """
    <style>
    .big-wave-container {
        position: relative;
        width: 100%;
        height: 180px;
        overflow: hidden;
        border-radius: 15px;
        margin: 10px 0 20px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background: #f0f2f6;
    }
    
    .big-wave {
        position: absolute;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(76, 175, 80, 0.8), rgba(76, 175, 80, 0.3));
        border-radius: 0 0 50% 50%;
        animation: big-wave 3s infinite ease-in-out;
        transform-origin: center bottom;
    }
    
    .big-wave:nth-child(2) {
        animation-delay: 0.6s;
        opacity: 0.6;
    }
    
    .big-wave:nth-child(3) {
        animation-delay: 1.2s;
        opacity: 0.4;
    }
    
    .big-wave-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #000;
        font-size: 32px;
        font-weight: bold;
        z-index: 10;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.7);
    }
    
    .big-wave-subtext {
        position: absolute;
        top: 65%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #333;
        font-size: 18px;
        z-index: 10;
    }
    
    @keyframes big-wave {
        0% {
            transform: translateY(80%) scaleY(0.2);
        }
        50% {
            transform: translateY(30%) scaleY(0.5);
        }
        100% {
            transform: translateY(80%) scaleY(0.2);
        }
    }
    </style>
    """
    
    big_wave_html = f"""
    {wave_container_css}
    <div class="big-wave-container">
        <div class="big-wave" style="bottom: {100-progression_pct}%;"></div>
        <div class="big-wave" style="bottom: {100-progression_pct}%;"></div>
        <div class="big-wave" style="bottom: {100-progression_pct}%;"></div>
        <div class="big-wave-text">{progression_pct:.1f}%</div>
        <div class="big-wave-subtext">des levés réalisés</div>
    </div>
    """
    
    col2.markdown(big_wave_html, unsafe_allow_html=True)
    
    # Informations complémentaires dans la troisième colonne
    dernier_mois_str = df["mois"].iloc[-1] if not df.empty else "N/A"
    col3.metric("Dernier mois", f"{dernier_mois_str}")
    
    # Calcul du rythme mensuel
    mois_ecoules = len(df)
    moyenne_mensuelle = realises_total / mois_ecoules if mois_ecoules > 0 else 0
    col3.metric("Moyenne mensuelle", f"{moyenne_mensuelle:.0f}")
    
    st.markdown("---")
    
    # Correction du problème des barres - Utilisation de données séparées
    st.subheader("📊 Suivi mensuel : Objectifs vs Réalisés")
    
    # Créer deux dataframes distincts pour éviter les problèmes de mise à l'échelle
    df_realises = df[["mois", "realises"]].copy()
    df_realises["Type"] = "Réalisés"
    df_realises = df_realises.rename(columns={"realises": "Nombre"})
    
    df_objectifs = df[["mois", "objectif_mensuel"]].copy()
    df_objectifs["Type"] = "Objectif mensuel"
    df_objectifs = df_objectifs.rename(columns={"objectif_mensuel": "Nombre"})
    
    # Fusionner les deux dataframes
    chart_data = pd.concat([df_realises, df_objectifs])
    
    # Créer le graphique avec Altair - Avec animation de vague pour les réalisations
    selection = alt.selection_point(fields=['mois'], bind='legend')
    
    # Créer le graphique de base
    bar_base = alt.Chart(chart_data).encode(
        x=alt.X("mois:N", title="Mois", sort=list(df["mois"])),
        y=alt.Y("Nombre:Q", title="Nombre d'inventaires"),
        tooltip=["mois:N", "Type:N", "Nombre:Q"]
    ).properties(height=400)
    
    # Barres pour les objectifs (en gris clair)
    objectif_bars = bar_base.transform_filter(
        alt.datum.Type == 'Objectif mensuel'
    ).mark_bar(color='lightgray').encode(
        opacity=alt.condition(selection, alt.value(0.7), alt.value(0.3))
    )
    
    # Barres pour les réalisations (en vert avec effet de vague)
    realises_bars = bar_base.transform_filter(
        alt.datum.Type == 'Réalisés'
    ).mark_bar(color='seagreen').encode(
        opacity=alt.condition(selection, alt.value(1), alt.value(0.5))
    )
    
    # Ajout de texte pour les valeurs
    text = bar_base.mark_text(
        align='center',
        baseline='middle',
        dy=-10,
        color='black'
    ).encode(
        text=alt.Text('Nombre:Q', format='.0f')
    )
    
    # Combiner les graphiques
    bar_chart = objectif_bars + realises_bars + text
    
    # Ajouter l'animation avec JavaScript (pour simuler l'effet de vague)
    st.markdown("""
    <style>
    @keyframes wave-animation {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
        100% { transform: translateY(0px); }
    }
    
    .wave-effect rect.seagreen {
        animation: wave-animation 2s infinite ease-in-out;
    }
    
    /* Appliquer un délai d'animation différent pour chaque barre */
    .wave-effect rect.seagreen:nth-child(1) { animation-delay: 0.0s; }
    .wave-effect rect.seagreen:nth-child(2) { animation-delay: 0.2s; }
    .wave-effect rect.seagreen:nth-child(3) { animation-delay: 0.4s; }
    .wave-effect rect.seagreen:nth-child(4) { animation-delay: 0.6s; }
    .wave-effect rect.seagreen:nth-child(5) { animation-delay: 0.8s; }
    .wave-effect rect.seagreen:nth-child(6) { animation-delay: 1.0s; }
    .wave-effect rect.seagreen:nth-child(7) { animation-delay: 1.2s; }
    .wave-effect rect.seagreen:nth-child(8) { animation-delay: 1.4s; }
    .wave-effect rect.seagreen:nth-child(9) { animation-delay: 1.6s; }
    .wave-effect rect.seagreen:nth-child(10) { animation-delay: 1.8s; }
    .wave-effect rect.seagreen:nth-child(11) { animation-delay: 2.0s; }
    .wave-effect rect.seagreen:nth-child(12) { animation-delay: 2.2s; }
    </style>
    
    <script>
    // Cette fonction sera exécutée une fois que le graphique est chargé
    function applyWaveEffect() {
        // Sélectionner tous les éléments rect avec la classe 'seagreen'
        let elements = document.querySelectorAll('.seagreen');
        
        // Ajouter une classe pour appliquer l'animation
        elements.forEach(el => {
            el.parentNode.classList.add('wave-effect');
        });
    }
    
    // Appliquer l'effet après un court délai pour s'assurer que le graphique est chargé
    setTimeout(applyWaveEffect, 1000);
    </script>
    """, unsafe_allow_html=True)
    
    # Afficher le graphique
    chart_container = st.container()
    with chart_container:
        st.altair_chart(bar_chart, use_container_width=True)
        
        # Créer un conteneur pour le texte explicatif sous le graphique
        with st.expander("Comment lire ce graphique", expanded=False):
            st.markdown("""
            - Les **barres vertes** représentent les levés **réalisés** chaque mois
            - Les **barres grises** représentent l'**objectif mensuel** à atteindre
            - L'**animation de vague** sur les barres vertes permet de visualiser la progression
            """)
    
    st.markdown("---")
    st.subheader("📈 Évolution de l'objectif cumulé")
    
    area_chart = alt.Chart(df).mark_area(opacity=0.3, color="lightblue").encode(
        x=alt.X("mois:N", title="Mois", sort=list(df["mois"])),
        y=alt.Y("objectif_total:Q", title="Objectif Cumulé"),
        tooltip=["mois:N", "objectif_total:Q"]
    ).properties(height=350)
    
    ligne_levés = alt.Chart(pd.DataFrame({
        "y": [realises_total],
        "text": ["Levés actuels"]
    })).mark_rule(color='green', strokeDash=[4, 4]).encode(
        y='y:Q'
    ) + alt.Chart(pd.DataFrame({
        "y": [realises_total],
        "text": [f"↳ {realises_total:,} levés"]
    })).mark_text(align="left", dx=5, dy=-5, color="green").encode(
        y="y:Q",
        text="text:N"
    )
    
    st.altair_chart(area_chart + ligne_levés, use_container_width=True)
    
    # Animation des vagues en bas de page
    st.markdown("---")
    st.subheader("🌊 Progression globale")
    
    # Créer les colonnes pour afficher trois vagues côte à côte
    wave_cols = st.columns(3)
    
    # Progression totale
    wave_cols[0].markdown(
        wave_animation(
            realises_total, 
            objectif_total, 
            f"{progression_pct:.1f}% total"
        ), 
        unsafe_allow_html=True
    )
    
    # Moyenne mensuelle (exemple)
    mois_ecoules = len(df)
    moyenne_mensuelle = realises_total / mois_ecoules if mois_ecoules > 0 else 0
    objectif_mensuel_moyen = df["objectif_mensuel"].mean()
    pourcentage_mensuel = (moyenne_mensuelle / objectif_mensuel_moyen * 100) if objectif_mensuel_moyen > 0 else 0
    
    wave_cols[1].markdown(
        wave_animation(
            moyenne_mensuelle, 
            objectif_mensuel_moyen, 
            f"{pourcentage_mensuel:.1f}% mensuel"
        ), 
        unsafe_allow_html=True
    )
    
    # Projection de fin d'année (exemple)
    projection_annuelle = (realises_total / mois_ecoules) * 12 if mois_ecoules > 0 else 0
    pct_projection = (projection_annuelle / objectif_total * 100) if objectif_total > 0 else 0
    
    wave_cols[2].markdown(
        wave_animation(
            projection_annuelle, 
            objectif_total, 
            f"{pct_projection:.1f}% projeté"
        ), 
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.subheader("📋 Données complètes")
    st.dataframe(df, use_container_width=True)

# Appel de la fonction principale
if __name__ == "__main__":
    afficher_projections_2025()
