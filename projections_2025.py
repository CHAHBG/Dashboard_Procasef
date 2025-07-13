# app.py  ───────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from functools import lru_cache
from datetime import datetime

# ───────────────────────────────────────────────────────────────────────
# 1. CONFIG GLOBALE ET PALETTE
# ───────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BET-PLUS | Projections 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PALETTE_LIGHT = {
    "primary":  "#FF9F1C",
    "secondary": "#FFBF69",
    "bg": "#FFFFFF",
    "fg": "#2F4858",
}
PALETTE_DARK = {
    "primary":  "#FFD166",
    "secondary": "#EF476F",
    "bg": "#0D1117",
    "fg": "#F0F6FC",
}

# Choix du thème
dark_mode = st.sidebar.toggle("🌙 Mode sombre", value=False)
P = PALETTE_DARK if dark_mode else PALETTE_LIGHT

# CSS minimaliste (variables + utility classes)
st.markdown(
    f"""
    <style>
        :root {{
            --primary:  {P['primary']};
            --secondary:{P['secondary']};
            --bg:       {P['bg']};
            --fg:       {P['fg']};
        }}
        html, body, [class*="css"]  {{
            background-color: var(--bg) !important;
            color: var(--fg);
            font-family: 'Poppins', sans-serif;
        }}
        .metric-card {{
            border-radius: 15px;
            padding: 1.25rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: var(--bg);
            text-align:center;
        }}
        .metric-card h2 {{margin:0.1rem 0 0.4rem 0;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# ───────────────────────────────────────────────────────────────────────
# 2. FONCTIONS UTILITAIRES
# ───────────────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode()
    )
    mapping = {
        "mois": "mois",
        "inventaires_mensuels_realises": "realises",
        "realises": "realises",
        "objectif_inventaires_mensuels": "objectif_mensuel",
        "objectif_mensuel": "objectif_mensuel",
        "objectif_inventaires_total": "objectif_total",
        "objectif_total": "objectif_total",
    }
    df = df.rename(columns={col: mapping.get(col, col) for col in df.columns})
    requises = {"mois", "realises", "objectif_mensuel", "objectif_total"}
    if not requises.issubset(df.columns):
        manquantes = ", ".join(requises - set(df.columns))
        st.error(f"Colonnes manquantes : {manquantes}")
        st.stop()
    df["realises"] = pd.to_numeric(df["realises"], errors="coerce").fillna(0)
    df["objectif_mensuel"] = pd.to_numeric(df["objectif_mensuel"], errors="coerce").fillna(0)
    df["objectif_total"] = pd.to_numeric(df["objectif_total"], errors="coerce").fillna(0)
    return df.dropna(subset=["mois"])

def meter_color(pct: float) -> str:
    if pct >= 100:
        return "#06D6A0"      # vert
    if pct >= 75:
        return "#FFD166"      # jaune
    if pct >= 50:
        return "#FF9F1C"      # orange
    return "#EF476F"          # rouge

# ───────────────────────────────────────────────────────────────────────
# 3. TABLEAU DE BORD
# ───────────────────────────────────────────────────────────────────────
def main():
    df = load_data("projections/Projections 2025.xlsx")
    realises_total = 31302
    objectif_total = df.objectif_total.iloc[-1]
    progression_pct = round(realises_total / objectif_total * 100, 1) if objectif_total else 0

    # HEADER
    st.title("📊 BET-PLUS | Projections des Inventaires 2025")
    st.caption(f"Dernière mise à jour : {datetime.now():%d %B %Y • %H:%M}")

    # ── 3.1 Métriques aggregées ───────────────────────────────────────
    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Inventaires réalisés", f"{realises_total:,}")
        col2.metric("Objectif 2025", f"{objectif_total:,}")
        col3.metric("Taux de réalisation", f"{progression_pct} %")

    st.divider()

    # ── 3.2 Graphiques interactifs dans des TABS ──────────────────────
    tab1, tab2, tab3 = st.tabs(["Performance mensuelle", "Objectif cumulé", "Radar mensuel"])

    # BARRES GROUPÉES
    with tab1:
        fig_bar = go.Figure()
        fig_bar.add_bar(
            x=df.mois, y=df.realises,
            marker_color=P["primary"], name="Réalisé",
            texttemplate="%{y:,}", textposition="auto"
        )
        fig_bar.add_bar(
            x=df.mois, y=df.objectif_mensuel,
            marker_color=P["secondary"], name="Objectif",
            texttemplate="%{y:,}", textposition="auto"
        )
        fig_bar.update_layout(
            barmode="group",
            margin=dict(t=30, b=10, l=10, r=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ÉVOLUTION CUMULÉE
    with tab2:
        fig_cumul = go.Figure()
        fig_cumul.add_scatter(
            x=df.mois, y=df.objectif_total, mode="lines+markers",
            name="Objectif cumulé", line=dict(color=P["secondary"], width=4)
        )
        fig_cumul.add_hline(
            y=realises_total, line=dict(color=P["primary"], dash="dash", width=4),
            annotation_text=f"Réalisés : {realises_total:,}", annotation_position="top right"
        )
        fig_cumul.update_layout(
            margin=dict(t=30, b=10, l=10, r=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_cumul, use_container_width=True)

    # RADAR
    with tab3:
        df["perf_pct"] = (df.realises / df.objectif_mensuel).fillna(0) * 100
        fig_radar = go.Figure()
        fig_radar.add_scatterpolar(
            r=df.perf_pct, theta=df.mois, fill="toself",
            line=dict(color=P["primary"]), fillcolor=P["primary"]+"55"
        )
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(range=[0, max(df.perf_pct.max()*1.1, 100)])),
            showlegend=False,
            margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()

    # ── 3.3 Insights et recommandations dynamiques ────────────────────
    meilleur = df.loc[df.perf_pct.idxmax()]
    restant = max(0, objectif_total - realises_total)

    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"""<div class="metric-card">
                <h4>Meilleure période</h4><h2>{meilleur.mois}</h2>
                <p>{meilleur.perf_pct:.1f} %</p></div>""", unsafe_allow_html=True)
        col2.markdown(f"""<div class="metric-card">
                <h4>Performance moyenne</h4><h2>{df.perf_pct.mean():.1f} %</h2> </div>""", unsafe_allow_html=True)
        col3.markdown(f"""<div class="metric-card">
                <h4>Inventaires restants</h4><h2>{restant:,}</h2></div>""", unsafe_allow_html=True)

    st.divider()

    # ── 3.4 Tableau détaillé (avec progress bar native) ───────────────
    df_display = df[["mois", "realises", "objectif_mensuel", "perf_pct"]].copy()
    df_display.columns = ["Mois", "Réalisé", "Objectif", "Performance %"]
    df_display = df_display.sort_values("Mois")
    st.dataframe(
        df_display.style.format({"Réalisé": "{:,.0f}", "Objectif": "{:,.0f}", "Performance %": "{:.1f} %"}),
        use_container_width=True,
    )

    # ── 3.5 Footer ────────────────────────────────────────────────────
    st.caption("© 2025 BET-PLUS | AUDET • Build v2.0")

# Point d’entrée
if __name__ == "__main__":
    main()
