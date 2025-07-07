import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Classe pour gérer le chargement des données avec une approche orientée objet"""
    
    def __init__(self):
        self.data_files = {
            'parcelles': 'parcelles.xlsx',
            'levee_commune': 'Levee par commune Terrain_URM.xlsx',
            'parcelles_terrain': 'Parcelles_terrain_periode.xlsx',
            'etapes': 'Etat des opérations Boundou-Mai 2025.xlsx',
            'post_traitement': 'Parcelles post traites par geom.xlsx'
        }
        self.cache = {}
    
    def get_data_path(self) -> Path:
        """Détermine le chemin des données selon l'environnement"""
        current_file = Path(__file__).resolve()
        project_root = current_file.parent
        
        possible_paths = [
            project_root / "data",
            project_root.parent / "data",
            Path(".") / "data",
            Path("./data"),
            Path("data")
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Dossier data trouvé: {path}")
                return path
        
        logger.warning("Aucun dossier data trouvé, utilisation du fallback")
        return possible_paths[0]
    
    def find_file_in_project(self, filename: str) -> Optional[str]:
        """Trouve un fichier dans tout le projet avec mise en cache"""
        if filename in self.cache:
            return self.cache[filename]
        
        # Recherche dans les emplacements prioritaires
        data_dir = self.get_data_path()
        priority_locations = [
            data_dir / filename,
            Path(".") / filename,
            Path("./data") / filename
        ]
        
        for path in priority_locations:
            if path.exists() and path.is_file():
                self.cache[filename] = str(path)
                return str(path)
        
        # Recherche récursive si pas trouvé
        for root_dir in [Path("."), Path(__file__).parent]:
            for path in root_dir.rglob(filename):
                if path.is_file():
                    self.cache[filename] = str(path)
                    return str(path)
        
        return None
    
    def load_excel_file(self, filename: str, process_func=None) -> pd.DataFrame:
        """Charge un fichier Excel avec traitement optionnel"""
        file_path = self.find_file_in_project(filename)
        
        if not file_path:
            logger.error(f"Fichier {filename} introuvable")
            return pd.DataFrame()
        
        try:
            df = pd.read_excel(file_path, engine="openpyxl")
            
            if process_func:
                df = process_func(df)
            
            logger.info(f"Fichier {filename} chargé avec succès depuis {file_path}")
            st.success(f"✅ {filename} chargé depuis: {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {filename}: {e}")
            st.error(f"❌ Erreur lors du chargement de {filename}: {e}")
            return pd.DataFrame()

# Instance globale du data loader
data_loader = DataLoader()

def process_parcelles_data(df: pd.DataFrame) -> pd.DataFrame:
    """Traite les données des parcelles"""
    df.columns = df.columns.str.lower()
    
    # Traitement NICAD
    df["nicad"] = df["nicad"].astype(str).str.strip().str.lower() == "oui"
    df["nicad"] = df["nicad"].map({True: "Avec NICAD", False: "Sans NICAD"})
    
    # Traitement délibération
    if "deliberee" in df.columns:
        df["deliberee"] = df["deliberee"].astype(str).str.strip().str.lower() == "oui"
        df["statut_deliberation"] = df["deliberee"].map({True: "Délibérée", False: "Non délibérée"})
    else:
        df["statut_deliberation"] = "Non délibérée"
    
    # Nettoyage des données
    df["superficie"] = pd.to_numeric(df["superficie"], errors="coerce")
    df["village"] = df["village"].fillna("Non spécifié").replace("", "Non spécifié")
    df["commune"] = df["commune"].fillna("Non spécifié").replace("", "Non spécifié")
    
    return df

def process_levee_commune_data(df: pd.DataFrame) -> pd.DataFrame:
    """Traite les données de levée par commune"""
    df.columns = df.columns.str.strip().str.lower()
    return df

def process_parcelles_terrain_data(df: pd.DataFrame) -> pd.DataFrame:
    """Traite les données parcelles terrain"""
    df.columns = df.columns.str.strip().str.lower()
    if 'date de debut' in df.columns:
        df['date de debut'] = pd.to_datetime(df['date de debut'], errors='coerce')
    if 'date de fin' in df.columns:
        df['date de fin'] = pd.to_datetime(df['date de fin'], errors='coerce')
    return df

def process_post_traitement_data(df: pd.DataFrame) -> pd.DataFrame:
    """Traite les données post-traitement"""
    df.columns = df.columns.str.strip().str.lower()
    return df

@st.cache_data
def charger_parcelles():
    """Charge les données des parcelles depuis le fichier Excel"""
    df = data_loader.load_excel_file(
        data_loader.data_files['parcelles'], 
        process_parcelles_data
    )
    
    if df.empty:
        # Retourner un DataFrame avec les colonnes attendues
        return pd.DataFrame(columns=[
            'commune', 'village', 'nicad', 'statut_deliberation', 'superficie', 'type_usag'
        ])
    
    return df

@st.cache_data
def charger_levee_par_commune():
    """Charge les données des levées par commune"""
    df = data_loader.load_excel_file(
        data_loader.data_files['levee_commune'], 
        process_levee_commune_data
    )
    
    if df.empty:
        st.warning("⚠️ Fichier levée par commune introuvable. Utilisation de données exemple.")
        return pd.DataFrame({
            'commune': ['Commune A', 'Commune B', 'Commune C'],
            'levee': [10, 15, 8],
            'total': [50, 60, 40]
        })
    
    return df

@st.cache_data
def charger_parcelles_terrain_periode():
    """Charge les données des parcelles terrain et leur période"""
    df = data_loader.load_excel_file(
        data_loader.data_files['parcelles_terrain'], 
        process_parcelles_terrain_data
    )
    
    if df.empty:
        st.warning("⚠️ Fichier parcelles terrain introuvable. Utilisation de données exemple.")
        return pd.DataFrame({
            'periode': ['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4'],
            'parcelles_terrain': [25, 35, 40, 30],
            'objectif': [30, 40, 45, 35]
        })
    
    return df

@st.cache_data
def charger_etapes():
    """Charge les données des étapes"""
    df = data_loader.load_excel_file(data_loader.data_files['etapes'])
    
    if df.empty:
        st.warning("⚠️ Fichier étapes introuvable. Utilisation de données exemple.")
        return pd.DataFrame({
            'etape': ['Identification', 'Levée topographique', 'Traitement', 'Validation'],
            'completees': [80, 65, 45, 20],
            'total': [100, 100, 100, 100],
            'pourcentage': [80, 65, 45, 20]
        })
    
    return df

@st.cache_data
def charger_parcelles_post_traitement():
    """Charge les données des parcelles post-traitées"""
    df = data_loader.load_excel_file(
        data_loader.data_files['post_traitement'], 
        process_post_traitement_data
    )
    
    if df.empty:
        st.warning("⚠️ Fichier post-traitement introuvable. Utilisation de données exemple.")
        return pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'commune': ['Commune A', 'Commune B', 'Commune C', 'Commune A', 'Commune B'],
            'statut': ['Traité', 'En cours', 'Traité', 'Traité', 'En attente']
        })
    
    return df

def interface_telechargement_fichier():
    """Interface pour le téléchargement de fichier avec diagnostic amélioré"""
    
    # Diagnostic de l'environnement
    with st.expander("🔍 Diagnostic de l'environnement", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Informations système:**")
            st.write(f"- Répertoire de travail: `{os.getcwd()}`")
            st.write(f"- Répertoire du script: `{Path(__file__).parent}`")
            st.write(f"- Python version: `{sys.version.split()[0]}`")
        
        with col2:
            st.write("**Structure des dossiers:**")
            current_dir = Path(".")
            directories = [p for p in current_dir.iterdir() if p.is_dir()]
            files = [p for p in current_dir.iterdir() if p.is_file()]
            
            st.write(f"- Dossiers: {len(directories)}")
            st.write(f"- Fichiers: {len(files)}")
            
            data_dir = current_dir / "data"
            if data_dir.exists():
                data_files = list(data_dir.glob("*.xlsx"))
                st.write(f"- Fichiers Excel dans data/: {len(data_files)}")
            else:
                st.write("- ❌ Dossier 'data' introuvable")
        
        # Vérification des fichiers requis
        st.write("**État des fichiers requis:**")
        for key, filename in data_loader.data_files.items():
            file_path = data_loader.find_file_in_project(filename)
            if file_path:
                st.write(f"- ✅ {filename}")
            else:
                st.write(f"- ❌ {filename}")
    
    # Interface de téléchargement
    st.markdown("---")
    st.subheader("📤 Télécharger le fichier des parcelles")
    
    uploaded_file = st.file_uploader(
        "Choisissez votre fichier Excel",
        type=['xlsx', 'xls'],
        help="Le fichier doit contenir les colonnes nécessaires pour l'analyse"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            df = process_parcelles_data(df)
            
            st.success("✅ Fichier chargé avec succès!")
            st.session_state['df_parcelles_uploaded'] = df
            
            # Afficher un aperçu
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lignes", df.shape[0])
            with col2:
                st.metric("Colonnes", df.shape[1])
            with col3:
                st.metric("Taille", f"{uploaded_file.size:,} bytes")
            
            with st.expander("Aperçu des données"):
                st.dataframe(df.head())
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement: {str(e)}")
            return pd.DataFrame()
    
    return pd.DataFrame()

def verifier_structure_fichiers():
    """Vérifie la présence de tous les fichiers nécessaires"""
    fichiers_requis = {
        'parcelles.xlsx': 'Données principales des parcelles',
        'Levee par commune Terrain_URM.xlsx': 'Données de levée par commune',
        'Parcelles_terrain_periode.xlsx': 'Données parcelles terrain par période',
        'Etat des opérations Boundou-Mai 2025.xlsx': 'Données des étapes du projet',
        'Parcelles post traites par geom.xlsx': 'Données parcelles post-traitées'
    }
    
    st.subheader("📋 État des fichiers de données")
    
    fichiers_manquants = []
    fichiers_presents = []
    
    for filename, description in fichiers_requis.items():
        file_path = data_loader.find_file_in_project(filename)
        if file_path:
            fichiers_presents.append(filename)
            st.success(f"✅ {filename}")
            st.caption(f"📍 {file_path}")
        else:
            fichiers_manquants.append(filename)
            st.error(f"❌ {filename}")
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fichiers trouvés", len(fichiers_presents))
    with col2:
        st.metric("Fichiers manquants", len(fichiers_manquants))
    with col3:
        st.metric("Taux de complétude", f"{len(fichiers_presents)/len(fichiers_requis)*100:.0f}%")
    
    if fichiers_manquants:
        st.warning(f"⚠️ {len(fichiers_manquants)} fichier(s) manquant(s)")
        
        with st.expander("💡 Guide d'organisation des fichiers"):
            st.markdown("""
            **Structure recommandée :**
            ```
            votre-projet/
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
            
            **Points clés pour Streamlit Cloud :**
            - Tous les fichiers doivent être sur GitHub
            - Vérifiez que `data/` n'est pas dans `.gitignore`
            - Limite de 100MB par fichier sur GitHub
            """)
    
    return len(fichiers_manquants) == 0

# Fonction utilitaire pour obtenir des informations sur les données
def get_data_info():
    """Retourne des informations sur l'état des données"""
    info = {
        'files_found': {},
        'total_files': len(data_loader.data_files),
        'files_missing': []
    }
    
    for key, filename in data_loader.data_files.items():
        file_path = data_loader.find_file_in_project(filename)
        if file_path:
            info['files_found'][key] = file_path
        else:
            info['files_missing'].append(filename)
    
    return info
