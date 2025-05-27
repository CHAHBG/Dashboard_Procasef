import streamlit as st
import pandas as pd
import altair as alt
import time


@st.cache_data
def charger_projections():
    df = pd.read_excel("projections/Projections 2025.xlsx", engine="openpyxl")
    # Nettoyage des noms de colonnes
    df.columns = df.columns.str.strip().str.lower()
    return df


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
            if cle in col:
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

    col1, col2 = st.columns(2)
    col1.metric("📌 Levés réalisés", f"{realises_total:,}", f"{progression_pct:.1f} %")

    # Jauge animée de progression
    progress_bar = col2.empty()
    for percent in range(0, int(progression_pct) + 1, 2):
        progress_bar.progress(min(percent / 100, 1.0), text=f"{percent}% de l'objectif atteint")
        time.sleep(0.1)

    st.markdown("---")

    st.subheader("📊 Suivi mensuel : Objectifs vs Réalisés")
    chart_data = df[["mois", "realises", "objectif_mensuel"]].melt(id_vars="mois", var_name="Type", value_name="Nombre")
    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X("mois:N", title="Mois", sort=list(df["mois"])),
        y=alt.Y("Nombre:Q", title="Nombre d'inventaires"),
        color=alt.Color("Type:N", title="", scale=alt.Scale(domain=["realises", "objectif_mensuel"], range=["seagreen", "lightgray"])),
        tooltip=["mois:N", "Type:N", "Nombre:Q"]
    ).properties(height=400)
    st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("---")

    st.subheader("📈 Évolution de l’objectif cumulé")
    area_chart = alt.Chart(df).mark_area(opacity=0.3, color="lightblue").encode(
        x=alt.X("mois:N", title="Mois",  sort=list(df["mois"])),
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

    st.markdown("---")
    st.subheader("📋 Données complètes")
    st.dataframe(df, use_container_width=True)
