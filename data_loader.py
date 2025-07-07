import streamlit as st
import pandas as pd
import os

@st.cache_data
def charger_parcelles():
    """Charge les données des parcelles depuis le fichier Excel"""
    
    # Chemins possibles étendus pour différents environnements
    chemins_possibles = [
        "data/parcelles.xlsx",
        "parcelles.xlsx",
        "./data/parcelles.xlsx",
        os.path.join(os.path.dirname(__file__), "data", "parcelles.xlsx"),
        os.path.join(os.path.dirname(__file__), "parcelles.xlsx"),
        os.path.abspath("data/parcelles.xlsx"),
        os.path.abspath("parcelles.xlsx")
    ]
    
    # Recherche automatique dans tous les sous-dossiers
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.lower() == 'parcelles.xlsx':
                chemins_possibles.append(os.path.join(root, file))
    
    # Éliminer les doublons
    chemins_possibles = list(set(chemins_possibles))
    
    for chemin in chemins_possibles:
        try:
            if os.path.exists(chemin):
                df = pd.read_excel(chemin, engine="openpyxl")
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
                
                st.success(f"✅ Données parcelles chargées depuis: {chemin}")
                return df
                
        except Exception as e:
            continue
    
    # Afficher les chemins testés pour débogage
    st.error("❌ Fichier 'parcelles.xlsx' introuvable")
    st.info("📁 Emplacements recherchés:")
    for chemin in chemins_possibles[:5]:  # Afficher seulement les 5 premiers
        st.write(f"- {chemin}")
    
    # Si aucun fichier n'est trouvé, retourner un DataFrame vide
    return pd.DataFrame(columns=[
        'commune', 'village', 'nicad', 'statut_deliberation', 'superficie', 'type_usag'
    ])

# Fonction utilitaire pour diagnostiquer l'environnement
def diagnostiquer_environnement():
    """Fonction utilitaire pour diagnostiquer l'environnement d'exécution"""
    st.subheader("🔍 Diagnostic de l'environnement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Informations système:**")
        st.write(f"- Répertoire de travail: `{os.getcwd()}`")
        st.write(f"- Fichier actuel: `{__file__}`")
        st.write(f"- Répertoire du script: `{os.path.dirname(__file__)}`")
    
    with col2:
        st.write("**Contenu des dossiers:**")
        st.write(f"- Racine: `{os.listdir('.')}`")
        if os.path.exists('data'):
            st.write(f"- Dossier data: `{os.listdir('data')}`")
        else:
            st.write("- ❌ Dossier 'data' introuvable")
    
    # Rechercher tous les fichiers Excel
    st.write("**Fichiers Excel détectés:**")
    fichiers_excel = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.xlsx', '.xls')):
                fichiers_excel.append(os.path.join(root, file))
    
    if fichiers_excel:
        for fichier in fichiers_excel:
            st.write(f"- ✅ {fichier}")
    else:
        st.write("- ❌ Aucun fichier Excel trouvé")
