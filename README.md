# Dashboard_Procasef
Dashboard pour le suivi des opérations à Boundou (PROCASEF)

# Description
Ce projet est une application web interactive développée en Python avec Streamlit. Elle permet de visualiser, suivre et analyser différentes données opérationnelles relatives au projet PROCASEF dans la région de Boundou.

Fonctionnalités principales
Répartition des parcelles
Visualisation de la distribution des parcelles sur le territoire.

État d’avancement
Suivi de la progression des différentes étapes du projet.

Projections 2025
Affichage de prévisions et d’analyses prospectives pour l’année 2025.

Répartition du genre
Analyse de la répartition hommes/femmes sur les parcelles ou au sein du projet.

Post-traitement
Analyses supplémentaires réalisées après la collecte des données.

Chaque fonctionnalité est accessible via un menu latéral interactif.

Prérequis
Python 3.7 ou supérieur
Les packages suivants :
streamlit
pandas
streamlit_option_menu
(Autres modules internes au projet)
Pour installer les dépendances principales :

bash
pip install -r requirements.txt
Utilisation
Clonez le dépôt :

bash
git clone https://github.com/CHAHBG/Dashboard_Procasef.git
cd Dashboard_Procasef
Lancez l’application :

bash
streamlit run dashboard.py
Ouvrez votre navigateur à l’adresse indiquée par Streamlit (souvent http://localhost:8501).

Organisation du projet
dashboard.py : Point d’entrée de l’application Streamlit.
repartParcelles.py, progression.py, projections_2025.py, genre_dashboard.py, post_traitement.py : Modules gérant chaque fonctionnalité du dashboard.
data_loader.py : Chargement et préparation des données.
logo/ : Images et logos utilisés dans l’interface.
Autres fichiers/dossiers selon l’évolution du projet.
Auteurs
CHAHBG
Licence
Ce projet est sous licence MIT (ou préciser la licence).

