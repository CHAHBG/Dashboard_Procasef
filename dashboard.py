import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
@st.cache_data
def charger_parcelles():
    df = pd.read_excel("parcelles.xlsx", engine="openpyxl")
    df.columns = df.columns.str.lower()  # uniformiser les noms de colonnes
    df["nicad"] = df["nicad"].astype(str).str.strip().str.lower() == "oui"
    df["superficie"] = pd.to_numeric(df["superficie"], errors="coerce")
    return df

df_parcelles = charger_parcelles()

st.title("📊 Tableau de Bord PROCASEF - Boundou")

# ========================
# Statistiques Globales
# ========================
st.subheader("📌 Statistiques Globales")

col1, col2, col3 = st.columns(3)
col1.metric("Nombre total de parcelles", len(df_parcelles))
col2.metric("Parcelles NICAD", df_parcelles["nicad"].sum())
col3.metric("Superficie totale (m²)", f"{df_parcelles['superficie'].sum():,.2f}")

# ========================
# Répartition NICAD globale
# ========================
fig_global = px.pie(df_parcelles, names="nicad", title="Répartition globale des parcelles NICAD",
                    labels={"nicad": "NICAD"})
st.plotly_chart(fig_global, use_container_width=True)

# ========================
# Répartition par Usage
# ========================
st.subheader("🏗️ Répartition par usage des parcelles")
fig_usage = px.pie(df_parcelles, names="usage", title="Répartition des usages",
                   labels={"usage": "Usage"})
st.plotly_chart(fig_usage, use_container_width=True)

# ========================
# Statistiques par village
# ========================
villages = df_parcelles["village"].dropna().unique()
village_selectionne = st.selectbox("📍 Choisir un village :", sorted(villages))

df_village = df_parcelles[df_parcelles["village"] == village_selectionne]

st.subheader(f"📍 Statistiques pour le village : {village_selectionne}")
col4, col5, col6 = st.columns(3)
col4.metric("Total parcelles", len(df_village))
col5.metric("Parcelles NICAD", df_village["nicad"].sum())
col6.metric("Superficie totale", f"{df_village['superficie'].sum():,.2f}")

fig_village = px.pie(df_village, names="nicad", title=f"Répartition NICAD - {village_selectionne}",
                     labels={"nicad": "NICAD"})
st.plotly_chart(fig_village, use_container_width=True)

# ========================
# Statistiques par commune
# ========================
st.subheader("🏘️ Répartition des parcelles par commune")

commune_data = df_parcelles.groupby(["commune", "nicad"]).size().reset_index(name="Nombre de parcelles")
fig_commune = px.bar(commune_data, x="commune", y="Nombre de parcelles", color="nicad",
                     barmode="group", title="Parcelles avec/sans NICAD par commune",
                     labels={"nicad": "NICAD"})
st.plotly_chart(fig_commune, use_container_width=True)

# ========================
# Données filtrées par village
# ========================
st.subheader("🧾 Données du village sélectionné")
st.dataframe(df_village, use_container_width=True)
