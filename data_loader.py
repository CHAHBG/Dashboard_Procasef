import streamlit as st
import pandas as pd
import os

# Module séparé pour le chargement des données
# Ceci évite les imports circulaires entre dashboard.py et post_traitement.py

@st.cache_data
def charger_parcelles():
    """Charge les données des parcelles depuis le fichier Excel"""
    chemins_possibles = [
        "data/parcelles.xlsx",
        "parcelles.xlsx",
        "./data/parcelles.xlsx"
    ]
    
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
                
                print(f"✅ Données parcelles chargées depuis: {chemin}")
                return df
        except Exception as e:
            continue
    
    # Si aucun fichier n'est trouvé, retourner un DataFrame vide avec les colonnes requises
    return pd.DataFrame(columns=[
        'commune', 'village', 'nicad', 'statut_deliberation', 'superficie', 'type_usag'
    ])

def interface_telechargement_fichier():
    """Interface séparée pour le téléchargement de fichier (non cachée)"""
    st.error("❌ Fichier 'parcelles.xlsx' introuvable")
    st.info("📁 Emplacements recherchés:")
    chemins_possibles = [
        "data/parcelles.xlsx",
        "parcelles.xlsx", 
        "./data/parcelles.xlsx"
    ]
    for chemin in chemins_possibles:
        st.write(f"- {chemin}")
    
    # Interface de téléchargement de fichier
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
            
            st.success("✅ Fichier chargé avec succès!")
            
            # Sauvegarder le fichier dans le cache de session
            st.session_state['df_parcelles_uploaded'] = df
            
            # Afficher un aperçu des données
            st.write("**Aperçu des données:**")
            st.write(f"- Nombre de lignes: {df.shape[0]}")
            st.write(f"- Nombre de colonnes: {df.shape[1]}")
            st.write("- Colonnes disponibles:", list(df.columns))
            
            # Afficher les premières lignes
            with st.expander("Voir les premières lignes"):
                st.dataframe(df.head())
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du fichier: {str(e)}")
            return pd.DataFrame(columns=[
                'commune', 'village', 'nicad', 'statut_deliberation', 'superficie', 'type_usag'
            ])
    
    # Retourner un DataFrame vide si aucun fichier n'est disponible
    return pd.DataFrame(columns=[
        'commune', 'village', 'nicad', 'statut_deliberation', 'superficie', 'type_usag'
    ])

@st.cache_data
def charger_levee_par_commune():
    """Charge les données des levées par commune depuis le fichier Excel"""
    chemins_possibles = [
        "data/Levee par commune Terrain_URM.xlsx",
        "Levee par commune Terrain_URM.xlsx",
        "./data/Levee par commune Terrain_URM.xlsx"
    ]
    
    for chemin in chemins_possibles:
        try:
            if os.path.exists(chemin):
                df = pd.read_excel(chemin, engine="openpyxl")
                df.columns = df.columns.str.strip().str.lower()
                print(f"✅ Données levée par commune chargées depuis: {chemin}")
                return df
        except Exception as e:
            continue
    
    st.warning("⚠️ Fichier 'Levee par commune Terrain_URM.xlsx' introuvable. Utilisation de données exemple.")
    # Retourner des données exemple
    return pd.DataFrame({
        'commune': ['Commune A', 'Commune B', 'Commune C'],
        'levee': [10, 15, 8],
        'total': [50, 60, 40]
    })

@st.cache_data
def charger_parcelles_terrain_periode():
    """Charge les données des parcelles terrain et leur période de levée"""
    chemins_possibles = [
        "data/Parcelles_terrain_periode.xlsx",
        "Parcelles_terrain_periode.xlsx",
        "./data/Parcelles_terrain_periode.xlsx"
    ]
    
    for chemin in chemins_possibles:
        try:
            if os.path.exists(chemin):
                df = pd.read_excel(chemin, engine="openpyxl")
                df.columns = df.columns.str.strip().str.lower()
                df['date de debut'] = pd.to_datetime(df['date de debut'], errors='coerce')
                df['date de fin'] = pd.to_datetime(df['date de fin'], errors='coerce')
                print(f"✅ Données parcelles terrain période chargées depuis: {chemin}")
                return df
        except Exception as e:
            continue
    
    st.warning("⚠️ Fichier 'Parcelles_terrain_periode.xlsx' introuvable. Utilisation de données exemple.")
    # Retourner des données exemple
    return pd.DataFrame({
        'periode': ['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4'],
        'parcelles_terrain': [25, 35, 40, 30],
        'objectif': [30, 40, 45, 35]
    })

@st.cache_data
def charger_etapes():
    """Charge les données des étapes depuis le fichier Excel"""
    chemins_possibles = [
        "data/Etat des opérations Boundou-Mai 2025.xlsx",
        "Etat des opérations Boundou-Mai 2025.xlsx",
        "./data/Etat des opérations Boundou-Mai 2025.xlsx"
    ]
    
    for chemin in chemins_possibles:
        try:
            if os.path.exists(chemin):
                df = pd.read_excel(chemin, engine="openpyxl")
                df.fillna("", inplace=True)
                print(f"✅ Données étapes chargées depuis: {chemin}")
                return df
        except Exception as e:
            continue
    
    st.warning("⚠️ Fichier 'Etat des opérations Boundou-Mai 2025.xlsx' introuvable. Utilisation de données exemple.")
    # Retourner des données exemple
    return pd.DataFrame({
        'etape': ['Identification', 'Levée topographique', 'Traitement', 'Validation'],
        'completees': [80, 65, 45, 20],
        'total': [100, 100, 100, 100],
        'pourcentage': [80, 65, 45, 20]
    })

@st.cache_data
def charger_parcelles_post_traitement():
    """Charge les données des parcelles post-traitées par géométrie"""
    chemins_possibles = [
        "data/Parcelles post traites par geom.xlsx",
        "Parcelles post traites par geom.xlsx",
        "./data/Parcelles post traites par geom.xlsx"
    ]
    
    for chemin in chemins_possibles:
        try:
            if os.path.exists(chemin):
                df = pd.read_excel(chemin, engine="openpyxl")
                df.columns = df.columns.str.strip().str.lower()
                print(f"✅ Données post-traitement chargées depuis: {chemin}")
                return df
        except Exception as e:
            continue
    
    st.warning("⚠️ Fichier 'Parcelles post traites par geom.xlsx' introuvable. Utilisation de données exemple.")
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'commune': ['Commune A', 'Commune B', 'Commune C', 'Commune A', 'Commune B'],
        'statut': ['Traité', 'En cours', 'Traité', 'Traité', 'En attente']
    })

def verifier_structure_fichiers():
    """Vérifie la présence de tous les fichiers Excel nécessaires"""
    fichiers_requis = {
        'data/parcelles.xlsx': 'Données principales des parcelles',
        'data/Levee par commune Terrain_URM.xlsx': 'Données de levée par commune',
        'data/Parcelles_terrain_periode.xlsx': 'Données parcelles terrain par période',
        'data/Etat des opérations Boundou-Mai 2025.xlsx': 'Données des étapes du projet',
        'data/Parcelles post traites par geom.xlsx': 'Données parcelles post-traitées'
    }
    
    st.subheader("📋 État des fichiers de données Excel")
    
    fichiers_manquants = []
    for fichier, description in fichiers_requis.items():
        if os.path.exists(fichier):
            st.success(f"✅ {os.path.basename(fichier)} - {description}")
        else:
            st.error(f"❌ {os.path.basename(fichier)} - {description}")
            fichiers_manquants.append(fichier)
    
    if fichiers_manquants:
        st.warning(f"⚠️ {len(fichiers_manquants)} fichier(s) manquant(s). Des données exemple seront utilisées.")
        
        with st.expander("💡 Comment organiser vos fichiers Excel"):
            st.markdown("""
            **Structure recommandée :**
            ```
            votre_projet/
            ├── dashboard.py
            ├── data_loader.py
            └── data/
                ├── parcelles.xlsx
                ├── Levee par commune Terrain_URM.xlsx
                ├── Parcelles_terrain_periode.xlsx
                ├── Etat des opérations Boundou-Mai 2025.xlsx
                └── Parcelles post traites par geom.xlsx
            ```
            
            **📌 Fichiers attendus :**
            - `parcelles.xlsx` : Fichier principal des parcelles
            - `Levee par commune Terrain_URM.xlsx` : Données de levée par commune  
            - `Parcelles_terrain_periode.xlsx` : Données terrain par période
            - `Etat des opérations Boundou-Mai 2025.xlsx` : État d'avancement
            - `Parcelles post traites par geom.xlsx` : Données post-traitées
            """)
    
    return len(fichiers_manquants) == 0
