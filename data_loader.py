import streamlit as st
import pandas as pd


# Module séparé pour le chargement des données
# Ceci évite les imports circulaires entre dashboard.py et post_traitement.py

@st.cache_data
def charger_parcelles():
    df = pd.read_excel("data/parcelles.xlsx", engine="openpyxl")
    df.columns = df.columns.str.lower()
    df["nicad"] = df["nicad"].astype(str).str.strip().str.lower() == "oui"
    df["nicad"] = df["nicad"].map({True: "Avec NICAD", False: "Sans NICAD"})

    if "deliberee" in df.columns:
        df["deliberee"] = df["deliberee"].astype(str).str.strip().str.lower() == "oui"
        df["statut_deliberation"] = df["deliberee"].map({True: "Délibérée", False: "Non délibérée"})
    else:
        df["statut_deliberation"] = "Non délibérée"

    df["superficie"] = pd.to_numeric(df["superficie"], errors="coerce")
    df["village"] = df["village"].fillna("Non spécifié").replace("", "Non spécifié")
    df["commune"] = df["commune"].fillna("Non spécifié").replace("", "Non spécifié")

    return df


@st.cache_data
def charger_levee_par_commune():
    """Charge les données des levées par commune depuis le fichier Excel"""
    try:
        df = pd.read_excel("data/Levee par commune Terrain_URM.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement de levée_par_commune.xlsx : {e}")
        return pd.DataFrame()


@st.cache_data
def charger_parcelles_terrain_periode():
    """Charge les données des parcelles terrain et leur période de levée"""
    try:
        df = pd.read_excel("data/Parcelles_terrain_periode.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        df['date de debut'] = pd.to_datetime(df['date de debut'], errors='coerce')
        df['date de fin'] = pd.to_datetime(df['date de fin'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement de levée_parcelles_par_periode.xlsx : {e}")
        return pd.DataFrame()


@st.cache_data
def charger_etapes():
    df = pd.read_excel("data/Etat des opérations Boundou-Mai 2025.xlsx", engine="openpyxl")
    df.fillna("", inplace=True)
    return df


@st.cache_data
def charger_parcelles_post_traitement():
    """Charge les données des parcelles post-traitées par géométrie"""
    try:
        df = pd.read_excel("data/Parcelles post traites par geom.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Erreur fichier parcelles post-traitées : {e}")
        return pd.DataFrame()