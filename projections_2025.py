import streamlit as st
import pandas as pd
import altair as alt
import time
import numpy as np

# Styles CSS améliorés pour les animations de vagues
st.markdown("""
<style>
.wave-container {
    position: relative;
    width: 100%;
    height: 120px;
    overflow: hidden;
    border-radius: 15px;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border: 2px solid #2196f3;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2);
}

.wave-fill {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    background: linear-gradient(45deg, #4fc3f7, #29b6f6, #03a9f4);
    transition: height 1s ease-in-out;
}

.wave-surface {
    position: absolute;
    top: -2px;
    left: 0;
    width: 200%;
    height: 8px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255,255,255,0.8), 
        transparent, 
        rgba(255,255,255,0.6), 
        transparent
    );
    transform-origin: center;
}

.wave-animation {
    animation: wave-movement 2s ease-in-out infinite;
}

.wave-stable {
    animation: none !important;
    background: linear-gradient(45deg, #4caf50, #66bb6a, #81c784) !important;
}

.wave-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    z-index: 10;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.progress-label {
    position: absolute;
    top: -25px;
    left: 50%;
    transform: translateX(-50%);
    color: #1976d2;
    font-size: 14px;
    font-weight: 600;
}

@keyframes wave-movement {
    0%, 100% {
        transform: translateX(-50%) scaleY(1);
    }
    25% {
        transform: translateX(-45%) scaleY(0.8);
    }
    50% {
        transform: translateX(-50%) scaleY(1.2);
    }
    75% {
        transform: translateX(-55%) scaleY(0.9);
    }
}

/* Animation alternative - Particules flottantes */
.particle-container {
    position: relative;
    width: 100%;
    height: 120px;
    overflow: hidden;
    border-radius: 15px;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    border: 2px solid #9c27b0;
}

.particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: #9c27b0;
    border-radius: 50%;
    animation: float 3s infinite ease-in-out;
}

.particle:nth-child(2) { animation-delay: 0.5s; }
.particle:nth-child(3) { animation-delay: 1s; }
.particle:nth-child(4) { animation-delay: 1.5s; }
.particle:nth-child(5) { animation-delay: 2s; }

@keyframes float {
    0%, 100% {
        transform: translateY(100px) rotate(0deg);
        opacity: 0;
    }
    50% {
        opacity: 1;
    }
    100% {
        transform: translateY(-20px) rotate(360deg);
        opacity: 0;
    }
}

/* Animation pulsation pour les métriques */
.metric-pulse {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(1);
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
    }
    50% {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.6);
    }
    100% {
        transform: scale(1);
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
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

def wave_progress_animation(value, max_value, text, label=""):
    """Crée une animation de vague où la hauteur représente le pourcentage"""
    percentage = min(value / max_value * 100, 100) if max_value > 0 else 0
    is_complete = percentage >= 100
    
    # Classes CSS conditionnelles
    wave_class = "wave-stable" if is_complete else "wave-animation"
    
    wave_html = f"""
    <div class="wave-container">
        <div class="progress-label">{label}</div>
        <div class="wave-fill {wave_class}" style="height: {percentage}%;">
            <div class="wave-surface"></div>
        </div>
        <div class="wave-text">{text}</div>
    </div>
    """
    return wave_html

def particle_animation(value, max_value, text, label=""):
    """Animation alternative avec des particules flottantes"""
    percentage = min(value / max_value * 100, 100) if max_value > 0 else 0
    particle_count = min(int(percentage / 20), 5)  # Maximum 5 particules
    
    particles = ""
    for i in range(particle_count):
        left = 20 + (i * 15)  # Espacement des particules
        particles += f'<div class="particle" style="left: {left}%; animation-delay: {i * 0.3}s;"></div>'
    
    particle_html = f"""
    <div class="particle-container">
        <div class="progress-label">{label}</div>
        {particles}
        <div class="wave-text">{text}</div>
    </div>
    """
    return particle_html

def afficher_projections_2025():
    st.header("📅 Projections des Inventaires - 2025")
    
    # Choix du type d'animation
    animation_type = st.selectbox(
        "🎨 Choisir le type d'animation",
        ["Vagues fluides", "Particules flottantes"],
        index=0
    )
    
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
    realises_total = 23693
    progression_pct = (realises_total / objectif_total) * 100 if objectif_total else 0
    
    # Affichage en deux colonnes avec métrique pulsante
    col1, col2 = st.columns(2)
    
    # Métrique avec effet pulsant si proche de l'objectif
    metric_class = "metric-pulse" if progression_pct > 80 else ""
    col1.markdown(f"""
    <div class="{metric_class}" style="padding: 20px; border-radius: 10px; background: linear-gradient(135deg, #e8f5e8, #c8e6c9);">
        <h3 style="color: #2e7d32; margin: 0;">📌 Levés réalisés</h3>
        <h1 style="color: #1b5e20; margin: 5px 0;">{realises_total:,}</h1>
        <p style="color: #388e3c; margin: 0; font-size: 18px;">↗️ {progression_pct:.1f}% de l'objectif</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Animation choisie dans la deuxième colonne
    if animation_type == "Vagues fluides":
        animation_html = wave_progress_animation(
            realises_total, 
            objectif_total, 
            f"{progression_pct:.1f}%", 
            "Progression globale"
        )
    else:
        animation_html = particle_animation(
            realises_total, 
            objectif_total, 
            f"{progression_pct:.1f}%", 
            "Progression globale"
        )
    
    col2.markdown(animation_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Graphiques existants
    st.subheader("📊 Suivi mensuel : Objectifs vs Réalisés")
    
    df_realises = df[["mois", "realises"]].copy()
    df_realises["Type"] = "Réalisés"
    df_realises = df_realises.rename(columns={"realises": "Nombre"})
    
    df_objectifs = df[["mois", "objectif_mensuel"]].copy()
    df_objectifs["Type"] = "Objectif mensuel"
    df_objectifs = df_objectifs.rename(columns={"objectif_mensuel": "Nombre"})
    
    chart_data = pd.concat([df_realises, df_objectifs])
    
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
    
    # Section des animations multiples
    st.markdown("---")
    st.subheader("🌊 Tableau de bord de progression")
    
    wave_cols = st.columns(3)
    
    # Calculs pour les différentes métriques
    mois_ecoules = len(df)
    moyenne_mensuelle = realises_total / mois_ecoules if mois_ecoules > 0 else 0
    objectif_mensuel_moyen = df["objectif_mensuel"].mean()
    pourcentage_mensuel = (moyenne_mensuelle / objectif_mensuel_moyen * 100) if objectif_mensuel_moyen > 0 else 0
    
    projection_annuelle = (realises_total / mois_ecoules) * 12 if mois_ecoules > 0 else 0
    pct_projection = (projection_annuelle / objectif_total * 100) if objectif_total > 0 else 0
    
    # Affichage avec le type d'animation choisi
    if animation_type == "Vagues fluides":
        wave_cols[0].markdown(
            wave_progress_animation(
                realises_total, 
                objectif_total, 
                f"{progression_pct:.1f}%",
                "🎯 Objectif global"
            ), 
            unsafe_allow_html=True
        )
        
        wave_cols[1].markdown(
            wave_progress_animation(
                moyenne_mensuelle, 
                objectif_mensuel_moyen, 
                f"{pourcentage_mensuel:.1f}%",
                "📊 Moyenne mensuelle"
            ), 
            unsafe_allow_html=True
        )
        
        wave_cols[2].markdown(
            wave_progress_animation(
                projection_annuelle, 
                objectif_total, 
                f"{pct_projection:.1f}%",
                "🔮 Projection annuelle"
            ), 
            unsafe_allow_html=True
        )
    else:
        wave_cols[0].markdown(
            particle_animation(
                realises_total, 
                objectif_total, 
                f"{progression_pct:.1f}%",
                "🎯 Objectif global"
            ), 
            unsafe_allow_html=True
        )
        
        wave_cols[1].markdown(
            particle_animation(
                moyenne_mensuelle, 
                objectif_mensuel_moyen, 
                f"{pourcentage_mensuel:.1f}%",
                "📊 Moyenne mensuelle"
            ), 
            unsafe_allow_html=True
        )
        
        wave_cols[2].markdown(
            particle_animation(
                projection_annuelle, 
                objectif_total, 
                f"{pct_projection:.1f}%",
                "🔮 Projection annuelle"
            ), 
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.subheader("📋 Données complètes")
    st.dataframe(df, use_container_width=True)

# Appel de la fonction principale
if __name__ == "__main__":
    afficher_projections_2025()
