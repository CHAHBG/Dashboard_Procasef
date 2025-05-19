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

# Ajout des styles pour l'animation de verre qui se remplit
st.markdown("""
<style>
.glass-container {
    position: relative;
    width: 100%;
    height: 150px;
    overflow: hidden;
    border-radius: 10px;
    margin-bottom: 20px;
    background: #f0f2f6;
    border: 3px solid #ddd;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.glass-fill {
    position: absolute;
    bottom: 0;
    width: 100%;
    background: linear-gradient(to bottom, rgba(30, 144, 255, 0.7), rgba(30, 144, 255, 0.9));
    border-radius: 0 0 7px 7px;
    transition: height 1s ease-in-out;
}

.glass-bubble {
    position: absolute;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 50%;
    animation: bubble 3s infinite;
}

.glass-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #000;
    font-size: 24px;
    font-weight: bold;
    z-index: 10;
    text-shadow: 1px 1px 2px white;
}

.glass-subtext {
    position: absolute;
    top: 70%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #333;
    font-size: 16px;
    z-index: 10;
    text-shadow: 1px 1px 2px white;
}

.glass-max-marker {
    position: absolute;
    width: 100%;
    height: 2px;
    background-color: #ff6347;
    z-index: 5;
}

@keyframes bubble {
    0% {
        transform: translateY(0) scale(1);
        opacity: 0;
    }
    50% {
        opacity: 0.7;
    }
    100% {
        transform: translateY(-100px) scale(0.5);
        opacity: 0;
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

def glass_animation(value, max_value, text, subtext=""):
    """Crée une animation de verre qui se remplit avec la valeur affichée"""
    # Calculer la hauteur de remplissage en fonction du pourcentage
    percentage = min(value / max_value * 100, 100) if max_value > 0 else 0
    fill_height = min(90, percentage * 0.9)  # Limite à 90% de la hauteur pour laisser un peu d'espace en haut
    
    # Créer des bulles aléatoires
    bubbles = ""
    for i in range(5):
        size = np.random.randint(5, 15)
        left = np.random.randint(10, 90)
        delay = np.random.randint(0, 30) / 10
        bubbles += f"""
        <div class="glass-bubble" style="width: {size}px; height: {size}px; left: {left}%; 
        bottom: {np.random.randint(10, int(fill_height))}%; animation-delay: {delay}s;"></div>
        """
    
    glass_html = f"""
    <div class="glass-container">
        <div class="glass-max-marker" style="bottom: 90%;"></div>
        <div class="glass-fill" style="height: {fill_height}%;">{bubbles}</div>
        <div class="glass-text">{text}</div>
        <div class="glass-subtext">{subtext}</div>
    </div>
    """
    return glass_html

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
    
    st.subheader("📌 Progression des levés réalisés")
    
    col1, col2, col3 = st.columns([2, 5, 2])
    
    # Affichage des métriques dans la première colonne
    col1.metric("Total réalisés", f"{realises_total:,}", f"{progression_pct:.1f} %")
    col1.metric("Objectif total", f"{objectif_total:,}")
    
    # Grand verre au centre
    big_glass_html = glass_animation(
        realises_total, 
        objectif_total, 
        f"{progression_pct:.1f}%", 
        "des levés réalisés"
    )
    
    col2.markdown(big_glass_html, unsafe_allow_html=True)
    
    # Informations complémentaires dans la troisième colonne
    dernier_mois_str = df["mois"].iloc[-1] if not df.empty else "N/A"
    col3.metric("Dernier mois", f"{dernier_mois_str}")
    
    # Calcul du rythme mensuel
    mois_ecoules = len(df)
    moyenne_mensuelle = realises_total / mois_ecoules if mois_ecoules > 0 else 0
    col3.metric("Moyenne mensuelle", f"{moyenne_mensuelle:.0f}")
    
    st.markdown("---")
    
    # Nouveau graphique représentant des verres pour chaque mois
    st.subheader("🥛 Suivi mensuel : Objectifs vs Réalisés")
    
    # Préparer les données pour le graphique "verre"
    months = df["mois"].tolist()
    cols_per_row = 6
    rows_needed = (len(months) + cols_per_row - 1) // cols_per_row
    
    for row in range(rows_needed):
        start_idx = row * cols_per_row
        end_idx = min(start_idx + cols_per_row, len(months))
        
        # Créer des colonnes pour chaque mois dans cette rangée
        month_cols = st.columns(cols_per_row)
        
        for i in range(start_idx, end_idx):
            month = months[i]
            realises = df.iloc[i]["realises"]
            objectif = df.iloc[i]["objectif_mensuel"]
            percent = (realises / objectif * 100) if objectif > 0 else 0
            
            month_cols[i % cols_per_row].markdown(f"<h4 style='text-align: center;'>{month}</h4>", unsafe_allow_html=True)
            
            # Créer un verre qui se remplit pour chaque mois
            glass_html = f"""
            <div class="glass-container" style="height: 120px;">
                <div class="glass-max-marker" style="bottom: 90%;"></div>
                <div class="glass-fill" style="height: {min(90, percent * 0.9)}%;">
                    <div class="glass-bubble" style="width: 8px; height: 8px; left: 30%; bottom: 20%;"></div>
                    <div class="glass-bubble" style="width: 5px; height: 5px; left: 70%; bottom: 40%;"></div>
                    <div class="glass-bubble" style="width: 6px; height: 6px; left: 40%; bottom: 60%;"></div>
                </div>
                <div class="glass-text">{percent:.1f}%</div>
                <div class="glass-subtext" style="font-size: 14px;">{realises}/{objectif}</div>
            </div>
            """
            month_cols[i % cols_per_row].markdown(glass_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Graphique en barres horizontales pour une meilleure lisibilité
    st.subheader("📊 Comparaison mensuelle détaillée")
    
    # Créer les données pour le graphique
    chart_data = pd.DataFrame({
        'mois': df['mois'],
        'Réalisés': df['realises'],
        'Objectif': df['objectif_mensuel'],
        'Pourcentage': (df['realises'] / df['objectif_mensuel'] * 100).fillna(0).round(1)
    })
    
    # Créer un graphique avec des barres horizontales
    horizontal_chart = alt.Chart(chart_data).transform_fold(
        ['Réalisés', 'Objectif'],
        as_=['Catégorie', 'Valeur']
    ).mark_bar().encode(
        y=alt.Y('mois:N', title='Mois', sort=list(df["mois"])),
        x=alt.X('Valeur:Q', title="Nombre d'inventaires"),
        color=alt.Color('Catégorie:N', scale=alt.Scale(
            domain=['Réalisés', 'Objectif'],
            range=['#1E90FF', '#dddddd']
        )),
        tooltip=['mois:N', 'Catégorie:N', 'Valeur:Q', alt.Tooltip('Pourcentage:Q', title='% Réalisés')]
    ).properties(
        height=alt.Step(30) * len(df)  # Ajuster la hauteur en fonction du nombre de mois
    )
    
    # Ajouter des étiquettes pour les pourcentages
    text_labels = alt.Chart(chart_data).mark_text(
        align='left',
        baseline='middle',
        dx=5,
        color='black'
    ).encode(
        y=alt.Y('mois:N', sort=list(df["mois"])),
        x='Réalisés:Q',
        text=alt.Text('Pourcentage:Q', format='.1f', suffix='%')
    )
    
    # Combiner les graphiques
    final_chart = horizontal_chart + text_labels
    
    st.altair_chart(final_chart, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📈 Évolution de l'objectif cumulé")
    
    # Créer un graphique à ligne pour l'évolution cumulée
    df_cumul = df.copy()
    df_cumul['Réalisés cumulés'] = df_cumul['realises'].cumsum()
    df_cumul['Objectif cumulé'] = df_cumul['objectif_mensuel'].cumsum()
    
    cumul_chart = alt.Chart(df_cumul).transform_fold(
        ['Réalisés cumulés', 'Objectif cumulé'],
        as_=['Série', 'Valeur']
    ).mark_line(point=True).encode(
        x=alt.X('mois:N', title='Mois', sort=list(df["mois"])),
        y=alt.Y('Valeur:Q', title='Inventaires cumulés'),
        color=alt.Color('Série:N', scale=alt.Scale(
            domain=['Réalisés cumulés', 'Objectif cumulé'],
            range=['#1E90FF', '#FF7F50']
        )),
        tooltip=['mois:N', 'Série:N', 'Valeur:Q']
    ).properties(height=400)
    
    st.altair_chart(cumul_chart, use_container_width=True)
    
    # Animation des verres en bas de page
    st.markdown("---")
    st.subheader("🥛 Progression globale")
    
    # Créer les colonnes pour afficher trois verres côte à côte
    glass_cols = st.columns(3)
    
    # Progression totale
    glass_cols[0].markdown(
        glass_animation(
            realises_total, 
            objectif_total, 
            f"{progression_pct:.1f}%", 
            "Progression totale"
        ), 
        unsafe_allow_html=True
    )
    
    # Moyenne mensuelle
    mois_ecoules = len(df)
    moyenne_mensuelle = realises_total / mois_ecoules if mois_ecoules > 0 else 0
    objectif_mensuel_moyen = df["objectif_mensuel"].mean()
    pourcentage_mensuel = (moyenne_mensuelle / objectif_mensuel_moyen * 100) if objectif_mensuel_moyen > 0 else 0
    
    glass_cols[1].markdown(
        glass_animation(
            moyenne_mensuelle, 
            objectif_mensuel_moyen, 
            f"{pourcentage_mensuel:.1f}%", 
            "Moyenne mensuelle"
        ), 
        unsafe_allow_html=True
    )
    
    # Projection de fin d'année
    projection_annuelle = (realises_total / mois_ecoules) * 12 if mois_ecoules > 0 else 0
    pct_projection = (projection_annuelle / objectif_total * 100) if objectif_total > 0 else 0
    
    glass_cols[2].markdown(
        glass_animation(
            projection_annuelle, 
            objectif_total, 
            f"{pct_projection:.1f}%", 
            "Projection annuelle"
        ), 
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.subheader("📋 Données complètes")
    st.dataframe(df, use_container_width=True)

# Appel de la fonction principale
if __name__ == "__main__":
    afficher_projections_2025()
