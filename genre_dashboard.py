import streamlit as st
import pandas as pd
import plotly.express as px
import time

@st.cache_data
def charger_donnees_genre():
    df_genre_trimestre = pd.read_excel("genre/Genre par trimestre.xlsx", engine="openpyxl")
    df_repartition_genre = pd.read_excel("genre/Repartition genre.xlsx", engine="openpyxl")
    df_genre_commune = pd.read_excel("genre/Genre par Commune.xlsx", engine="openpyxl")
    return df_genre_trimestre, df_repartition_genre, df_genre_commune

def personnaliser_graphique(fig, titre=None):
    fig.update_layout(
        template="simple_white",
        title=titre,
        title_font=dict(size=20, color="gray"),
        legend_title_text="Genre",
        legend=dict(x=1, y=1),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14)
    )
    return fig

def afficher_jauge_objectif(pourcentage, seuil=30):
    jauge = st.empty()
    statut = st.empty()
    for i in range(0, int(pourcentage) + 1):
        barres = int(i / 5) * "█" + int((100 - i) / 5) * "░"
        jauge.markdown(f"**🟡 Femmes : {i} %**\n\n`{barres}`")
        time.sleep(0.05)
    if pourcentage >= seuil:
        statut.success("✅ Objectif atteint !")
    else:
        statut.error(f"❌ Objectif non atteint ({pourcentage}% < {seuil}%)")

def afficher_repartition_genre():
    df_genre_trimestre, df_repartition_genre, df_genre_commune = charger_donnees_genre()

    st.title("👫🏿 Répartition du genre")

    with st.expander("1️⃣ Statistiques globales et objectif 🔍", expanded=True):
        col1, col2, col3 = st.columns(3)
        total_femmes = int(df_repartition_genre[df_repartition_genre["Genre"] == "Femme"]["Total_Nombre"].iloc[0])
        total_hommes = int(df_repartition_genre[df_repartition_genre["Genre"] == "Homme"]["Total_Nombre"].iloc[0])
        total = total_femmes + total_hommes
        pourcentage_femmes = round((total_femmes / total) * 100)

        with col1:
            st.metric("🟡 Femmes", f"{total_femmes:,}")
        with col2:
            st.metric("🔵 Hommes", f"{total_hommes:,}")
        with col3:
            st.metric("👥 Total", f"{total:,}")

        st.subheader("🎯 Objectif de 30 % de femmes")
        afficher_jauge_objectif(pourcentage_femmes)

        fig_pie = px.pie(
            df_repartition_genre,
            names="Genre",
            values="Total_Nombre",
            color="Genre",
            color_discrete_map={"Homme": "steelblue", "Femme": "goldenrod"},
            hole=0.4
        )
        fig_pie = personnaliser_graphique(fig_pie, "📊 Répartition globale 🔵🟡")
        st.plotly_chart(fig_pie, use_container_width=True)

    with st.expander("2️⃣ Répartition par commune 🗺️", expanded=False):
        st.subheader("📍 Analyse par commune individuelle")

        communes = df_genre_commune["communeSenegal"].unique()
        commune_selection = st.selectbox("🔍 Choisir une commune", communes)

        df_commune = df_genre_commune[df_genre_commune["communeSenegal"] == commune_selection]
        femmes_c = int(df_commune["Femme"].iloc[0])
        hommes_c = int(df_commune["Homme"].iloc[0])
        total_c = femmes_c + hommes_c
        pourcentage_femmes_c = round((femmes_c / total_c) * 100)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.write(f"### 📍 {commune_selection}")
            afficher_jauge_objectif(pourcentage_femmes_c)

        with col2:
            df_temp = pd.DataFrame({
                "Genre": ["Femme", "Homme"],
                "Nombre": [femmes_c, hommes_c]
            })
            fig_com = px.pie(
                df_temp,
                names="Genre",
                values="Nombre",
                color="Genre",
                color_discrete_map={"Femme": "goldenrod", "Homme": "steelblue"},
                hole=0.3
            )
            fig_com.update_traces(pull=[0.1, 0], hoverinfo='label+percent+value')
            st.plotly_chart(fig_com, use_container_width=True)

        st.markdown("---")
        st.subheader("🌍 Répartition globale par commune")

        df_long = df_genre_commune.melt(
            id_vars=["communeSenegal"],
            value_vars=["Femme", "Homme"],
            var_name="Genre",
            value_name="Nombre"
        )
        fig_all_communes = px.bar(
            df_long,
            x="communeSenegal",
            y="Nombre",
            color="Genre",
            barmode="stack",
            color_discrete_map={"Femme": "goldenrod", "Homme": "steelblue"}
        )
        fig_all_communes = personnaliser_graphique(fig_all_communes, "Répartition du genre par commune")
        st.plotly_chart(fig_all_communes, use_container_width=True)

    with st.expander("3️⃣ Répartition par type de parcelle", expanded=False):
        st.subheader("📌 👫🏿")
        types = ["Individuel", "Collectif", "Mandataires"]
        for type_ in types:
            col_nb = f"{type_}_Nombre"
            fig = px.bar(
                df_repartition_genre,
                x="Genre",
                y=col_nb,
                color="Genre",
                text=col_nb,
                color_discrete_map={"Femme": "goldenrod", "Homme": "steelblue"}
            )
            titre = f"{type_} : Nombre par genre"
            fig = personnaliser_graphique(fig, titre)
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("4️⃣ Évolution trimestrielle 📆", expanded=False):
        fig_evol = px.area(
            df_genre_trimestre,
            x="PeriodeTrimestrielle",
            y=["Femme", "Homme"],
            labels={"value": "Nombre", "variable": "Genre"},
            color_discrete_map={"Femme": "goldenrod", "Homme": "steelblue"},
            markers=True
        )
        fig_evol = personnaliser_graphique(fig_evol, "📈 Évolution trimestrielle 🔵🟡")
        st.plotly_chart(fig_evol, use_container_width=True)

# Appel principal
if __name__ == "__main__":
    afficher_repartition_genre()
