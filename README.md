# 📊 Dashboard_Procasef

**Dashboard pour le suivi des opérations du projet PROCASEF à Boundou**

---

## 📝 Description

Ce projet est une application web interactive développée en **Python** avec **Streamlit**.  
Elle permet de **visualiser**, **suivre** et **analyser** les données opérationnelles du projet **PROCASEF** dans la région de **Boundou**.

---

## 🚀 Fonctionnalités principales

- **Répartition des parcelles**  
  Visualisation de la distribution des parcelles sur le territoire.

- **État d’avancement**  
  Suivi de la progression des différentes étapes du projet.

- **Projections 2025**  
  Affichage de prévisions et d’analyses prospectives pour l’année 2025.

- **Répartition du genre**  
  Analyse de la répartition hommes/femmes sur les parcelles ou au sein du projet.

- **Post-traitement**  
  Analyses supplémentaires réalisées après la collecte des données.

📌 Chaque fonctionnalité est accessible via un **menu latéral interactif**.

---

## ⚙️ Prérequis

- **Python** 3.7 ou supérieur  
- Packages nécessaires :
  - `streamlit`
  - `pandas`
  - `streamlit_option_menu`
  - *(Autres modules internes au projet)*

### 💾 Installation des dépendances

```bash
pip install -r requirements.txt
```

---

## ▶️ Utilisation

1. **Clonez le dépôt :**

```bash
git clone https://github.com/CHAHBG/Dashboard_Procasef.git
cd Dashboard_Procasef
```

2. **Lancez l’application Streamlit :**

```bash
streamlit run dashboard.py
```

3. **Ouvrez votre navigateur** à l’adresse indiquée par Streamlit (souvent `http://localhost:8501`).

---

## 🗂️ Organisation du projet

| Fichier / Dossier         | Description                                                 |
|--------------------------|-------------------------------------------------------------|
| `dashboard.py`           | Point d’entrée principal de l’application Streamlit         |
| `repartParcelles.py`     | Module de visualisation de la répartition des parcelles     |
| `progression.py`         | Suivi de l’état d’avancement                                |
| `projections_2025.py`    | Analyse des projections à l’horizon 2025                    |
| `genre_dashboard.py`     | Analyse de la répartition du genre                          |
| `post_traitement.py`     | Module de post-traitement des données                       |
| `data_loader.py`         | Chargement et préparation des données                       |
| `logo/`                  | Dossier contenant les logos et images utilisées             |
| *(Autres fichiers)*      | En fonction de l’évolution du projet                        |

---

## 👤 Auteurs

- [CHAHBG](https://github.com/CHAHBG)

---

## 📄 Licence

Ce projet est sous licence **MIT**.  
Voir le fichier [LICENSE](LICENSE) pour plus d’informations.

---

> Pour toute suggestion, contribution ou amélioration, n’hésitez pas à ouvrir une **issue** ou une **pull request**.
