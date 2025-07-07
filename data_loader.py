import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path

# Module séparé pour le chargement des données
# Optimisé pour Streamlit Cloud et GitHub

def get_data_path():
    """Détermine le chemin des données selon l'environnement"""
    # Chemin du fichier actuel
    current_file = Path(__file__).resolve()
    project_root = current_file.parent
    
    # Chemins possibles pour Streamlit Cloud
    possible_paths = [
        project_root / "data",
        project_root.parent / "data",
        Path(".") / "data",
        Path("./data"),
        Path("data")
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Si aucun dossier data n'est trouvé, retourner le premier comme fallback
    return possible_paths[0]

def find_file_in_project(filename):
    """Trouve un fichier dans tout le projet"""
    # Commencer par le répertoire courant
    current_dir = Path(".")
    
    # Rechercher dans tous les sous-dossiers
    for path in current_dir.rglob(filename):
        if path.is_file():
            return str(path)
    
    # Rechercher aussi depuis le répertoire du script
    script_dir = Path(__file__).parent
    for path in script_dir.rglob(filename):
        if path.is_file():
            return str(path)
    
    return None

@st.cache_data
def charger_parcelles():
    """Charge les données des parcelles depuis le fichier Excel - Version Streamlit Cloud"""
    
    # Stratégie 1: Chercher dans les emplacements standards
    data_dir = get_data_path()
    chemins_standards = [
        data_dir / "parcelles.xlsx",
        Path("data") / "parcelles.xlsx",
        Path(".") / "data" / "parcelles.xlsx",
        Path("parcelles.xlsx"),
        Path("./parcelles.xlsx")
    ]
    
    # Convertir en chaînes et ajouter les chemins absolus
    chemins_possibles = []
    for chemin in chemins_standards:
        chemins_possibles.append(str(chemin))
        chemins_possibles.append(str(chemin.resolve()))
    
    # Stratégie 2: Recherche automatique dans tout le projet
    fichier_trouve = find_file_in_project("parcelles.xlsx")
    if fichier_trouve:
        chemins_possibles.insert(0, fichier_trouve)
    
    # Éliminer les doublons tout en préservant l'ordre
    chemins_uniques = []
    for chemin in chemins_possibles:
        if chemin not in chemins_uniques:
            chemins_uniques.append(chemin)
    
    # Essayer de charger le fichier
    for chemin in chemins_uniques:
        try:
            chemin_path = Path(chemin)
            if chemin_path.exists() and chemin_path.is_file():
                df = pd.read_excel(str(chemin_path), engine="openpyxl")
                
                # Traitement des données
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
    
    # Si aucun fichier n'est trouvé, retourner un DataFrame vide
    return pd.DataFrame(columns=[
        'commune', 'village', 'nicad', 'statut_deliberation', 'superficie', 'type_usag'
    ])

def interface_telechargement_fichier():
    """Interface séparée pour le téléchargement de fichier (non cachée)"""
    
    # Diagnostic de l'environnement
    with st.expander("🔍 Diagnostic de l'environnement", expanded=False):
        st.write("**Informations système:**")
        st.write(f"- Répertoire de travail: `{os.getcwd()}`")
        st.write(f"- Répertoire du script: `{Path(__file__).parent}`")
        st.write(f"- Python version: `{sys.version}`")
        
        st.write("**Structure des dossiers:**")
        current_dir = Path(".")
        st.write(f"- Contenu racine: `{list(current_dir.iterdir())}`")
        
        data_dir = current_dir / "data"
        if data_dir.exists():
            st.write(f"- Contenu dossier data: `{list(data_dir.iterdir())}`")
        else:
            st.write("- ❌ Dossier 'data' introuvable")
        
        # Rechercher tous les fichiers Excel
        st.write("**Fichiers Excel détectés:**")
        fichiers_excel = list(current_dir.rglob("*.xlsx")) + list(current_dir.rglob("*.xls"))
        if fichiers_excel:
            for fichier in fichiers_excel:
                st.write(f"- ✅ {fichier}")
        else:
            st.write("- ❌ Aucun fichier Excel trouvé")
    
    st.error("❌ Fichier 'parcelles.xlsx' introuvable")
    st.info("📁 Emplacements recherchés:")
    
    # Afficher les chemins testés
    data_dir = get_data_path()
    chemins_affiches = [
        str(data_dir / "parcelles.xlsx"),
        "data/parcelles.xlsx",
        "./data/parcelles.xlsx",
        "parcelles.xlsx"
    ]
    
    for chemin in chemins_affiches:
        existe = Path(chemin).exists()
        status = "✅" if existe else "❌"
        st.write(f"{status} {chemin}")
    
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
    
    return pd.DataFrame(columns=[
        'commune', 'village', 'nicad', 'statut_deliberation', 'superficie', 'type_usag'
    ])

@st.cache_data
def charger_levee_par_commune():
    """Charge les données des levées par commune depuis le fichier Excel"""
    filename = "Levee par commune Terrain_URM.xlsx"
    
    # Recherche automatique du fichier
    fichier_trouve = find_file_in_project(filename)
    if fichier_trouve:
        try:
            df = pd.read_excel(fichier_trouve, engine="openpyxl")
            df.columns = df.columns.str.strip().str.lower()
            st.success(f"✅ Données levée par commune chargées depuis: {fichier_trouve}")
            return df
        except Exception as e:
            st.warning(f"⚠️ Erreur lors du chargement de {filename}: {e}")
    
    st.warning(f"⚠️ Fichier '{filename}' introuvable. Utilisation de données exemple.")
    return pd.DataFrame({
        'commune': ['Commune A', 'Commune B', 'Commune C'],
        'levee': [10, 15, 8],
        'total': [50, 60, 40]
    })

@st.cache_data
def charger_parcelles_terrain_periode():
    """Charge les données des parcelles terrain et leur période de levée"""
    filename = "Parcelles_terrain_periode.xlsx"
    
    # Recherche automatique du fichier
    fichier_trouve = find_file_in_project(filename)
    if fichier_trouve:
        try:
            df = pd.read_excel(fichier_trouve, engine="openpyxl")
            df.columns = df.columns.str.strip().str.lower()
            df['date de debut'] = pd.to_datetime(df['date de debut'], errors='coerce')
            df['date de fin'] = pd.to_datetime(df['date de fin'], errors='coerce')
            st.success(f"✅ Données parcelles terrain période chargées depuis: {fichier_trouve}")
            return df
        except Exception as e:
            st.warning(f"⚠️ Erreur lors du chargement de {filename}: {e}")
    
    st.warning(f"⚠️ Fichier '{filename}' introuvable. Utilisation de données exemple.")
    return pd.DataFrame({
        'periode': ['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4'],
        'parcelles_terrain': [25, 35, 40, 30],
        'objectif': [30, 40, 45, 35]
    })

@st.cache_data
def charger_etapes():
    """Charge les données des étapes depuis le fichier Excel"""
    filename = "Etat des opérations Boundou-Mai 2025.xlsx"
    
    # Recherche automatique du fichier
    fichier_trouve = find_file_in_project(filename)
    if fichier_trouve:
        try:
            df = pd.read_excel(fichier_trouve, engine="openpyxl")
            df.fillna("", inplace=True)
            st.success(f"✅ Données étapes chargées depuis: {fichier_trouve}")
            return df
        except Exception as e:
            st.warning(f"⚠️ Erreur lors du chargement de {filename}: {e}")
    
    st.warning(f"⚠️ Fichier '{filename}' introuvable. Utilisation de données exemple.")
    return pd.DataFrame({
        'etape': ['Identification', 'Levée topographique', 'Traitement', 'Validation'],
        'completees': [80, 65, 45, 20],
        'total': [100, 100, 100, 100],
        'pourcentage': [80, 65, 45, 20]
    })

@st.cache_data
def charger_parcelles_post_traitement():
    """Charge les données des parcelles post-traitées par géométrie"""
    filename = "Parcelles post traites par geom.xlsx"
    
    # Recherche automatique du fichier
    fichier_trouve = find_file_in_project(filename)
    if fichier_trouve:
        try:
            df = pd.read_excel(fichier_trouve, engine="openpyxl")
            df.columns = df.columns.str.strip().str.lower()
            st.success(f"✅ Données post-traitement chargées depuis: {fichier_trouve}")
            return df
        except Exception as e:
            st.warning(f"⚠️ Erreur lors du chargement de {filename}: {e}")
    
    st.warning(f"⚠️ Fichier '{filename}' introuvable. Utilisation de données exemple.")
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'commune': ['Commune A', 'Commune B', 'Commune C', 'Commune A', 'Commune B'],
        'statut': ['Traité', 'En cours', 'Traité', 'Traité', 'En attente']
    })

def verifier_structure_fichiers():
    """Vérifie la présence de tous les fichiers Excel nécessaires"""
    fichiers_requis = {
        'parcelles.xlsx': 'Données principales des parcelles',
        'Levee par commune Terrain_URM.xlsx': 'Données de levée par commune',
        'Parcelles_terrain_periode.xlsx': 'Données parcelles terrain par période',
        'Etat des opérations Boundou-Mai 2025.xlsx': 'Données des étapes du projet',
        'Parcelles post traites par geom.xlsx': 'Données parcelles post-traitées'
    }
    
    st.subheader("📋 État des fichiers de données Excel")
    
    fichiers_manquants = []
    for filename, description in fichiers_requis.items():
        fichier_trouve = find_file_in_project(filename)
        if fichier_trouve:
            st.success(f"✅ {filename} - {description}")
            st.caption(f"📍 Emplacement: {fichier_trouve}")
        else:
            st.error(f"❌ {filename} - {description}")
            fichiers_manquants.append(filename)
    
    if fichiers_manquants:
        st.warning(f"⚠️ {len(fichiers_manquants)} fichier(s) manquant(s). Des données exemple seront utilisées.")
        
        with st.expander("💡 Comment organiser vos fichiers Excel"):
            st.markdown("""
            **Structure recommandée pour GitHub + Streamlit Cloud :**
            ```
            votre-repo/
            ├── dashboard.py
            ├── data_loader.py
            ├── requirements.txt
            └── data/
                ├── parcelles.xlsx
                ├── Levee par commune Terrain_URM.xlsx
                ├── Parcelles_terrain_periode.xlsx
                ├── Etat des opérations Boundou-Mai 2025.xlsx
                └── Parcelles post traites par geom.xlsx
            ```
            
            **⚠️ Points importants pour Streamlit Cloud :**
            - Tous les fichiers doivent être committés sur GitHub
            - Vérifiez que le dossier `data/` n'est pas dans `.gitignore`
            - Les fichiers Excel doivent être < 100MB (limite GitHub)
            - Utilisez Git LFS pour les gros fichiers si nécessaire
            """)
    
    return len(fichiers_manquants) == 0
