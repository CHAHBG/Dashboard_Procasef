import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def charger_levee_par_commune():
    try:
        df = pd.read_excel("data/Levee par commune Terrain_URM.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        df = df.fillna({'commune': 'Non spécifié'})
        return df
    except Exception as e:
        st.error(f"Erreur fichier levée commune : {e}")
        return pd.DataFrame()

@st.cache_data
def charger_parcelles_terrain_periode():
    try:
        df = pd.read_excel("data/Parcelles_terrain_periode.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        for col in ['date de debut', 'date de fin']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erreur fichier parcelles période : {e}")
        return pd.DataFrame()

def afficher_post_traitement(df_post_traitement):
    st.subheader("⚙️ Module de Post-traitement")

    df_levee = charger_levee_par_commune()
    df_parcelles = charger_parcelles_terrain_periode()

    tab1, tab2 = st.tabs(["🏘️ Communes & Régions", "📆 Par périodes"])

    with tab1:
        st.markdown("### 📊 Comparaison des Parcelles Terrain vs URM")
        communes = df_levee['commune'].unique()
        commune_sel = st.selectbox("Filtrer par commune", ["Toutes"] + list(communes))

        df_filtre = df_levee if commune_sel == "Toutes" else df_levee[df_levee['commune'] == commune_sel]

        if "parcelles terrain" in df_filtre.columns and "parcelles delimitées et enquetées (fourni par l'opérateur)(urm)" in df_filtre.columns:
            fig = go.Figure([
                go.Bar(name="Parcelles Terrain", x=df_filtre['commune'], y=df_filtre['parcelles terrain']),
                go.Bar(name="Parcelles URM", x=df_filtre['commune'], y=df_filtre["parcelles delimitées et enquetées (fourni par l'opérateur)(urm)"])
            ])
            fig.update_layout(barmode='group', xaxis_tickangle=-45,
                              title="Comparaison par commune", legend_title="Type")
            st.plotly_chart(fig, use_container_width=True)

            if 'region' in df_levee.columns:
                st.markdown("### 🌍 Comparaison par région")
                df_region = df_levee.groupby('region')[
                    ['parcelles terrain', "parcelles delimitées et enquetées (fourni par l'opérateur)(urm)"]
                ].sum().reset_index()

                fig2 = go.Figure([
                    go.Bar(name="Parcelles Terrain", x=df_region['region'], y=df_region['parcelles terrain']),
                    go.Bar(name="Parcelles URM", x=df_region['region'], y=df_region["parcelles delimitées et enquetées (fourni par l'opérateur)(urm)"])
                ])
                fig2.update_layout(barmode='group', xaxis_tickangle=-45,
                                   title="Comparaison par région", legend_title="Type")
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("### 📆 Évolution temporelle des levées")
        if df_parcelles.empty:
            st.warning("Aucune donnée disponible.")
            return

        commune_options = df_parcelles['commune'].dropna().unique()
        commune_sel = st.selectbox("Choisir une commune", ["Toutes"] + sorted(commune_options))

        # Conversion explicite des dates
        date_min = df_parcelles['date de debut'].min()
        date_max = df_parcelles['date de fin'].max()

        # Vérification des dates valides
        if pd.isnull(date_min) or pd.isnull(date_max):
            st.warning("Dates invalides ou manquantes dans les données.")
            return

        date_min = pd.to_datetime(date_min).to_pydatetime()
        date_max = pd.to_datetime(date_max).to_pydatetime()

        if date_min >= date_max:
            st.warning("La date de début est postérieure à la date de fin.")
            return

        # Slider de dates corrigé
        date_range = st.slider(
            "Filtrer par période",
            min_value=date_min,
            max_value=date_max,
            value=(date_min, date_max),
            format="YYYY-MM-DD"
        )

        df_filtre = df_parcelles[
            (df_parcelles['date de debut'] >= date_range[0]) &
            (df_parcelles['date de fin'] <= date_range[1])
        ]
        if commune_sel != "Toutes":
            df_filtre = df_filtre[df_filtre['commune'] == commune_sel]

        if df_filtre.empty:
            st.warning("Aucune donnée pour cette sélection.")
            return

        df_filtre['periode'] = df_filtre['date de debut'].dt.to_period('M').astype(str)

        evolution = df_filtre.groupby('periode').size().reset_index(name='Nombre')
        fig = px.line(evolution, x='periode', y='Nombre', markers=True,
                      title="Évolution des levées par période")
        st.plotly_chart(fig, use_container_width=True)

        if 'statut' in df_filtre.columns:
            statuts = df_filtre.groupby(['periode', 'statut']).size().reset_index(name='count')
            fig2 = px.line(statuts, x='periode', y='count', color='statut', markers=True,
                           title="Évolution par statut")
            st.plotly_chart(fig2, use_container_width=True)

        with st.expander("📋 Voir les données filtrées"):
            st.dataframe(df_filtre)
