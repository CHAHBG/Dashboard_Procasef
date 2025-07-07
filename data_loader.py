import streamlit as st
import pandas as pd
import os

def charger_parcelles():
    """
    Charge les données des parcelles depuis le fichier Excel,
    ou propose à l'utilisateur de charger un fichier si absent.
    """
    chemins_possibles = [
        "data/parcelles.xlsx",
        "parcelles.xlsx",
        "./data/parcelles.xlsx"
    ]
    for chemin in chemins_possibles:
        try:
            if os.path.exists(chemin):
                df = pd.read_excel(chemin, engine="openpyxl")
                df = nettoyer_parcelles(df)
                st.success(f"✅ Données parcelles chargées depuis: {chemin}")
                return df
        except Exception as e:
            continue

    # Si aucun fichier trouvé, demander à l'utilisateur d'en charger un
    st.error("❌ Fichier 'parcelles.xlsx' introuvable")
    st.info("📁 Emplacements recherchés:")
    for chemin in chemins_possibles:
        st.write(f"- {chemin}")
    st.markdown("---")
    st.subheader("📤 Télécharger le fichier des parcelles")
    uploaded_file = st.file_uploader(
        "Choisissez votre fichier Excel contenant les données des parcelles",
        type=['xlsx', 'xls'],
        help="Le fichier doit contenir les colonnes nécessaires pour l'analyse des parcelles"
    )
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            df = nettoyer_parcelles(df)
            st.success("✅ Fichier chargé avec succès!")
            st.write("**Aperçu des données:**")
            st.write(f"- Nombre de lignes: {df.shape[0]}")
            st.write(f"- Nombre de colonnes: {df.shape[1]}")
            st.write("- Colonnes disponibles:", list(df.columns))
            with st.expander("Voir les premières lignes"):
                st.dataframe(df.head())
            return df
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du fichier: {str(e)}")
            return pd.DataFrame()
    return pd.DataFrame()

def nettoyer_parcelles(df):
    # Nettoyage et harmonisation des colonnes
    df.columns = df.columns.str.lower().str.strip()
    if "nicad" in df.columns:
        df["nicad"] = df["nicad"].astype(str).str.strip().str.lower() == "oui"
        df["nicad"] = df["nicad"].map({True: "Avec NICAD", False: "Sans NICAD"})
    else:
        df["nicad"] = "Sans NICAD"
    if "deliberee" in df.columns:
        df["deliberee"] = df["deliberee"].astype(str).str.strip().str.lower() == "oui"
        df["statut_deliberation"] = df["deliberee"].map({True: "Délibérée", False: "Non délibérée"})
    else:
        df["statut_deliberation"] = "Non délibérée"
    if "superficie" in df.columns:
        df["superficie"] = pd.to_numeric(df["superficie"], errors="coerce")
    else:
        df["superficie"] = 0
    if "village" in df.columns:
        df["village"] = df["village"].fillna("Non spécifié").replace("", "Non spécifié")
    else:
        df["village"] = "Non spécifié"
    if "commune" in df.columns:
        df["commune"] = df["commune"].fillna("Non spécifié").replace("", "Non spécifié")
    else:
        df["commune"] = "Non spécifié"
    return df
