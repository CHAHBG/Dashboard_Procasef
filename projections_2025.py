import streamlit as st


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
    
    # Affichage en deux colonnes
    col1, col2 = st.columns(2)
    
    # Affichage du métrique dans la première colonne
    col1.metric("📌 Levés réalisés", f"{realises_total:,}", f"{progression_pct:.1f} %")
    
    # Animation de vague personnalisée dans la deuxième colonne
    wave_html = wave_animation(realises_total, objectif_total, f"{progression_pct:.1f}% atteint")
    col2.markdown(wave_html, unsafe_allow_html=True)
    
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
    
    # Créer le graphique avec Altair
    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X("mois:N", title="Mois", sort=list(df["mois"])),
        y=alt.Y("Nombre:Q", title="Nombre d'inventaires"),
        color=alt.Color(
            "Type:N", 
            title="",
            scale=alt.Scale(
                domain=["Réalisés", "Objectif mensuel"],
                range=["seagreen", "lightgray"]
            )
        ),
        tooltip=["mois:N", "Type:N", "Nombre:Q"]
    ).properties(height=400)
    
    st.altair_chart(bar_chart, use_container_width=True)
    
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
