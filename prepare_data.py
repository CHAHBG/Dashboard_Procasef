import pandas as pd
import os


# === Chargement Excel avec dtypes forcés ===
def charger_fichier(fichier):
    return pd.read_excel(fichier, dtype={'Num_parcel': str, 'Num_parcel_2': str, 'Nicad': str})


# === Harmoniser les noms de colonnes ===
def harmoniser_colonnes(df):
    df.columns = df.columns.str.strip()

    if 'Num_parcel_2' in df.columns:
        df['id_parcelle'] = df['Num_parcel_2'].astype(str)
    elif 'Num_parcel' in df.columns:
        df['id_parcelle'] = df['Num_parcel'].astype(str)
    elif 'idup' in df.columns:
        df['id_parcelle'] = df['idup'].astype(str)
    else:
        raise ValueError("Aucune colonne d'identifiant trouvée (Num_parcel, Num_parcel_2 ou idup)")

    df = df.rename(columns={
        'communeSenegal': 'commune',
        'nicad': 'Nicad'
    })

    if 'Village' not in df.columns:
        df['Village'] = "Non spécifié"

    # IMPORTANT : Examiner toutes les colonnes potentiellement contenant des NICADs
    nicad_candidates = [col for col in df.columns if 'nicad' in col.lower() or 'nica' in col.lower()]
    if nicad_candidates:
        print(f"   ➤ Colonnes potentiellement NICAD trouvées: {nicad_candidates}")

    return df


# === Marquer la correspondance URM (NICAD oui/non) ===
def ajouter_nicad(df_kobo, df_urm):
    df_kobo['id_parcelle'] = df_kobo['id_parcelle'].astype(str)
    df_urm['id_parcelle'] = df_urm['id_parcelle'].astype(str)

    # Compter les correspondances pour le débogage
    nb_matches = sum(df_kobo["id_parcelle"].isin(df_urm["id_parcelle"]))
    print(f"   ➤ Nombre de correspondances trouvées: {nb_matches}")

    df_kobo["nicad"] = df_kobo["id_parcelle"].isin(df_urm["id_parcelle"]).map({True: "Oui", False: "Non"})

    # IMPORTANT: Essayer d'extraire les vraies valeurs de NICAD depuis df_urm
    if "Nicad" in df_urm.columns:
        # Créer un dictionnaire de mapping id_parcelle -> Nicad
        nicad_mapping = df_urm.set_index('id_parcelle')['Nicad'].to_dict()
        print(f"   ➤ Nombre de NICADs dans le mapping: {len(nicad_mapping)}")
        print(f"   ➤ Exemples de NICADs du mapping: {list(nicad_mapping.values())[:5]}")

        # Appliquer le mapping pour ajouter les NICADs
        df_kobo['Nicad_real'] = df_kobo['id_parcelle'].map(nicad_mapping)

        # Compter combien de NICADs ont été ajoutés
        nb_nicads_added = df_kobo['Nicad_real'].notna().sum()
        print(f"   ➤ NICADs ajoutés: {nb_nicads_added}")

        # Copier vers la colonne Nicad si elle existe déjà
        if 'Nicad' in df_kobo.columns:
            df_kobo['Nicad'] = df_kobo['Nicad_real'].fillna(df_kobo['Nicad'])
            df_kobo.drop(columns=['Nicad_real'], inplace=True)
        else:
            df_kobo['Nicad'] = df_kobo['Nicad_real']
            df_kobo.drop(columns=['Nicad_real'], inplace=True)

    return df_kobo


# === Ajouter les attributs depuis URM avec fallback sur Kobo ===
def completer_attributs(df_kobo, df_urm, attributs, mapping_cols=None):
    if mapping_cols is None:
        mapping_cols = {}
    df_urm_subset = df_urm[['id_parcelle'] + [mapping_cols.get(a, a) for a in attributs if
                                              mapping_cols.get(a, a) in df_urm.columns]].copy()

    # Ajouter Nicad si présent pour le transfert
    if 'Nicad' in df_urm.columns and 'Nicad' not in attributs:
        df_urm_subset['Nicad'] = df_urm['Nicad']

    df_merge = df_kobo.merge(df_urm_subset, on='id_parcelle', how='left', suffixes=('', '_urm'))

    for attr in attributs:
        col_source = mapping_cols.get(attr, attr)
        col_urm = f"{col_source}_urm"
        if col_urm in df_merge.columns:
            df_merge[attr] = df_merge[col_urm].combine_first(df_merge.get(attr)).fillna("Non spécifié")
            df_merge.drop(columns=[col_urm], inplace=True)
        else:
            df_merge[attr] = df_merge.get(attr, "Non spécifié").fillna("Non spécifié")

    # Transférer également Nicad si disponible
    if 'Nicad_urm' in df_merge.columns:
        df_merge['Nicad'] = df_merge['Nicad_urm'].combine_first(df_merge.get('Nicad')).fillna("")
        df_merge.drop(columns=['Nicad_urm'], inplace=True)

    return df_merge


# === Fonction de normalisation de NICAD ===
def normaliser_nicad(nicad_series):
    if nicad_series is None:
        return None
    # Convertir en string
    nicad_series = nicad_series.astype(str)
    # Enlever les espaces et convertir en majuscules
    nicad_series = nicad_series.str.strip().str.upper()
    # Remplacer les valeurs comme 'nan', 'None', etc.
    nicad_series = nicad_series.replace(['NAN', 'NONE', 'NA', 'N/A', '<NA>', 'NULL', '', '.'], None)
    return nicad_series


# === Afficher des informations de debug sur les NICADs ===
def debug_nicad(df, nom_df):
    print(f"\n🔍 Debug NICAD pour {nom_df}:")
    if 'Nicad' in df.columns:
        print(f"   ➤ Nombre de NICADs non-null: {df['Nicad'].notna().sum()}")
        print(f"   ➤ Exemples de NICADs (premiers 5): {df['Nicad'].dropna().head(5).tolist()}")
    else:
        print(f"   ❌ Colonne 'Nicad' absente!")

    # Examiner toutes les colonnes contenant des NICADs potentiels
    nicad_candidates = [col for col in df.columns if 'nicad' in col.lower() or 'nica' in col.lower()]
    for col in nicad_candidates:
        if col != 'Nicad':
            print(f"   ➤ Colonne potentielle '{col}': {df[col].notna().sum()} valeurs non-null")
            print(f"   ➤ Exemples (premiers 5): {df[col].dropna().head(5).tolist()}")


# === Examiner les colonnes d'un DataFrame ===
def examiner_colonnes(df, nom_df):
    print(f"\n📋 Colonnes de {nom_df}:")
    print(f"   ➤ Nombre total de colonnes: {len(df.columns)}")
    print(f"   ➤ Liste des colonnes: {df.columns.tolist()}")

    # Extraire quelques statistiques sur les colonnes
    for col in df.columns:
        nb_not_null = df[col].notna().sum()
        pct_not_null = 100 * nb_not_null / len(df) if len(df) > 0 else 0
        print(f"   ➤ {col}: {nb_not_null}/{len(df)} valeurs non-null ({pct_not_null:.1f}%)")
        if nb_not_null > 0:
            # Afficher les premières valeurs non-null
            values = df[col].dropna().head(3).tolist()
            print(f"      Exemples: {values}")


# === Chemins des fichiers ===
print("🔍 Chargement des fichiers source...")
kobo_individuels = charger_fichier(r"C:\Users\ASUS\Downloads\Enquete_Foncière-Parcelles_Individuelles_05052025.xlsx")
kobo_collectifs = charger_fichier(r"C:\Users\ASUS\Downloads\Enquete_Foncière-Parcelles_Collectives_05052025.xlsx")
urm_individuels = charger_fichier(
    r"C:\Users\ASUS\Downloads\3.a Validation par URM\3.a Validation par URM\All NICADS\GPKG Merged\parcelles_individuelles_nicad_Lot5_32.xlsx")
urm_collectifs = charger_fichier(
    r"C:\Users\ASUS\Downloads\3.a Validation par URM\3.a Validation par URM\All NICADS\GPKG Merged\parcelles_collectives_nicad_Lot5_32.xlsx")

ndoga_init_ind = charger_fichier(
    r"C:\Users\ASUS\Downloads\VALIDATION_NICAD_BND Bon (1)\1.a.Topologie avec jointure (2)\parcelles_individuelles_1234.xlsx")
ndoga_init_col = charger_fichier(
    r"C:\Users\ASUS\Downloads\VALIDATION_NICAD_BND Bon (1)\1.a.Topologie avec jointure (2)\parcelles_collectives_1234.xlsx")
ndoga_nicad_ind = charger_fichier(
    r"C:\Users\ASUS\Downloads\VALIDATION_NICAD_BND Bon (1)\VALIDATION_NICAD\Ndoga_Individuelles_NICAD_LOT1_2_3_4.xlsx")
ndoga_nicad_col = charger_fichier(
    r"C:\Users\ASUS\Downloads\VALIDATION_NICAD_BND Bon (1)\VALIDATION_NICAD\Ndoga_Collectives_NICAD_LOT1_2_3_4.xlsx")

# === Analyse des structures de fichiers ===
print("\n🔍 Analyse des structures de fichiers pour trouver les NICADs...")
examiner_colonnes(urm_individuels, "urm_individuels")
examiner_colonnes(urm_collectifs, "urm_collectifs")
examiner_colonnes(ndoga_nicad_ind, "ndoga_nicad_ind")
examiner_colonnes(ndoga_nicad_col, "ndoga_nicad_col")

# === Harmonisation des colonnes ===
print("\n🔍 Harmonisation des colonnes...")
df_kobo_ind = harmoniser_colonnes(kobo_individuels)
df_kobo_col = harmoniser_colonnes(kobo_collectifs)
df_urm_ind = harmoniser_colonnes(urm_individuels)
df_urm_col = harmoniser_colonnes(urm_collectifs)
df_ndoga_init_ind = harmoniser_colonnes(ndoga_init_ind)
df_ndoga_init_col = harmoniser_colonnes(ndoga_init_col)
df_ndoga_nicad_ind = harmoniser_colonnes(ndoga_nicad_ind)
df_ndoga_nicad_col = harmoniser_colonnes(ndoga_nicad_col)

try:
    print("\n🔍 Traitement des parcelles individuelles Kobo...")
    df_kobo_ind = ajouter_nicad(df_kobo_ind, df_urm_ind)
    df_kobo_ind = completer_attributs(df_kobo_ind, df_urm_ind, ['superficie', 'type_usag'])
    df_kobo_ind['type_usa'] = "Non applicable"

    print("\n🔍 Traitement des parcelles collectives Kobo...")
    df_kobo_col = ajouter_nicad(df_kobo_col, df_urm_col)
    df_kobo_col = completer_attributs(df_kobo_col, df_urm_col, ['superficie', 'type_usa'])
    df_kobo_col['type_usag'] = "Non applicable"

    print("\n🔍 Traitement des parcelles individuelles Ndoga...")
    df_ndoga_init_ind = ajouter_nicad(df_ndoga_init_ind, df_ndoga_nicad_ind)
    df_ndoga_init_ind = completer_attributs(
        df_ndoga_init_ind, df_ndoga_nicad_ind,
        ['superficie', 'type_usag'],
        mapping_cols={'type_usag': 'typ_usage'}
    )
    df_ndoga_init_ind['type_usa'] = "Non applicable"

    print("\n🔍 Traitement des parcelles collectives Ndoga...")
    df_ndoga_init_col = ajouter_nicad(df_ndoga_init_col, df_ndoga_nicad_col)
    df_ndoga_init_col = completer_attributs(
        df_ndoga_init_col, df_ndoga_nicad_col,
        ['superficie', 'type_usa'],
        mapping_cols={'type_usa': 'typ_usage'}
    )
    df_ndoga_init_col['type_usag'] = "Non applicable"

    # === Fusions ===
    print("\n🔍 Fusion des DataFrames...")
    df_kobo_final = pd.concat([df_kobo_ind, df_kobo_col], ignore_index=True)
    df_ndoga_final = pd.concat([df_ndoga_init_ind, df_ndoga_init_col], ignore_index=True)
    df_global_final = pd.concat([df_kobo_final, df_ndoga_final], ignore_index=True)

    # Debug après fusion
    debug_nicad(df_global_final, "df_global_final après fusion")

    # === Chargement des délibérations avec Nicad et Autorité ===
    print("\n🔍 Chargement des fichiers de délibération...")
    delib_indiv = pd.read_excel(r"C:\Users\ASUS\Downloads\Deliberation_bandafassi\Delib_Individuel.xlsx",
                                dtype={'Nicad': str})
    delib_collec = pd.read_excel(r"C:\Users\ASUS\Downloads\Deliberation_bandafassi\Delib_Collectif.xlsx",
                                 dtype={'Nicad': str})

    # Afficher les en-têtes pour vérifier les noms de colonnes
    print(f"Colonnes dans delib_indiv: {delib_indiv.columns.tolist()}")
    print(f"Colonnes dans delib_collec: {delib_collec.columns.tolist()}")

    # Nombre de lignes dans chaque fichier de délibération
    print(f"Nombre d'entrées delib_indiv: {len(delib_indiv)}")
    print(f"Nombre d'entrées delib_collec: {len(delib_collec)}")

    # Rechercher et afficher explicitement la colonne NICAD
    nicad_col_indiv = [col for col in delib_indiv.columns if 'nicad' in col.lower()]
    nicad_col_collec = [col for col in delib_collec.columns if 'nicad' in col.lower()]
    print(f"Colonnes potentielles pour NICAD dans delib_indiv: {nicad_col_indiv}")
    print(f"Colonnes potentielles pour NICAD dans delib_collec: {nicad_col_collec}")

    # Trouver la colonne d'autorité
    autorite_col_indiv = [col for col in delib_indiv.columns if 'autorit' in col.lower() or 'autor' in col.lower()]
    autorite_col_collec = [col for col in delib_collec.columns if 'autorit' in col.lower() or 'autor' in col.lower()]
    print(f"Colonnes potentielles pour Autorité dans delib_indiv: {autorite_col_indiv}")
    print(f"Colonnes potentielles pour Autorité dans delib_collec: {autorite_col_collec}")

    # Adaptation pour utiliser les bonnes colonnes trouvées
    nicad_col_name_indiv = 'Nicad' if 'Nicad' in delib_indiv.columns else (
        nicad_col_indiv[0] if nicad_col_indiv else None)
    nicad_col_name_collec = 'Nicad' if 'Nicad' in delib_collec.columns else (
        nicad_col_collec[0] if nicad_col_collec else None)
    autorite_col_name_indiv = 'Autorité' if 'Autorité' in delib_indiv.columns else (
        autorite_col_indiv[0] if autorite_col_indiv else None)
    autorite_col_name_collec = 'Autorité' if 'Autorité' in delib_collec.columns else (
        autorite_col_collec[0] if autorite_col_collec else None)

    # Vérifier si nous avons trouvé les colonnes nécessaires
    if not nicad_col_name_indiv or not nicad_col_name_collec:
        print("❌ ERREUR: Impossible de trouver les colonnes NICAD dans les fichiers de délibération!")

    if not autorite_col_name_indiv or not autorite_col_name_collec:
        print("⚠️ AVERTISSEMENT: Impossible de trouver les colonnes Autorité dans les fichiers de délibération.")
        autorite_col_name_indiv = autorite_col_name_indiv or "Autorité"  # Valeur par défaut
        autorite_col_name_collec = autorite_col_name_collec or "Autorité"  # Valeur par défaut

    # Renommer les colonnes pour standardisation
    if nicad_col_name_indiv and nicad_col_name_indiv != 'Nicad':
        delib_indiv = delib_indiv.rename(columns={nicad_col_name_indiv: 'Nicad'})
    if nicad_col_name_collec and nicad_col_name_collec != 'Nicad':
        delib_collec = delib_collec.rename(columns={nicad_col_name_collec: 'Nicad'})

    if autorite_col_name_indiv and autorite_col_name_indiv != 'Autorité':
        delib_indiv = delib_indiv.rename(columns={autorite_col_name_indiv: 'Autorité'})
    if autorite_col_name_collec and autorite_col_name_collec != 'Autorité':
        delib_collec = delib_collec.rename(columns={autorite_col_name_collec: 'Autorité'})

    # Fusionner les délibérations
    delib_global = pd.concat([delib_indiv, delib_collec], ignore_index=True)

    # Debug des NICADs
    debug_nicad(delib_global, "delib_global avant normalisation")
    debug_nicad(df_global_final, "df_global_final avant normalisation")

    # Normaliser les NICADs pour éviter les problèmes de correspondance
    delib_global['Nicad'] = normaliser_nicad(delib_global['Nicad'])
    df_global_final['Nicad'] = normaliser_nicad(df_global_final['Nicad'])

    # Debug après normalisation
    debug_nicad(delib_global, "delib_global après normalisation")
    debug_nicad(df_global_final, "df_global_final après normalisation")

    # Vérifier les NICADs communs pour débogage
    nicads_delib = set(delib_global['Nicad'].dropna().unique())
    nicads_global = set(df_global_final['Nicad'].dropna().unique())
    nicads_communs = nicads_delib.intersection(nicads_global)
    print(f"\n🧩 Analyse NICAD:")
    print(f"   ➤ Nombre de NICADs uniques dans les délibérations: {len(nicads_delib)}")
    print(f"   ➤ Nombre de NICADs uniques dans les parcelles: {len(nicads_global)}")
    print(f"   ➤ Nombre de NICADs communs: {len(nicads_communs)}")

    # Liste des NICADs communs (limité pour ne pas surcharger la sortie)
    if nicads_communs:
        print(f"   ➤ Exemples de NICADs communs: {list(nicads_communs)[:10]}")

    # === Marquage "delibere" + ajout autorité ===
    print("\n🔍 Ajout des informations de délibération...")
    # Utiliser une fusion left avec seules les colonnes nécessaires
    delib_subset = delib_global[['Nicad', 'Autorité']].dropna(subset=['Nicad']).rename(
        columns={'Autorité': 'autorite_delib'}
    )

    # Utiliser merge avec indicateur pour voir quelles lignes correspondent
    df_merged = df_global_final.merge(
        delib_subset,
        on='Nicad',
        how='left',
        indicator=True
    )

    # Créer la colonne 'delibere' basée sur l'indicateur de fusion
    df_merged['delibere'] = df_merged['_merge'].map({'left_only': 'Non', 'both': 'Oui'})
    df_merged.drop(columns=['_merge'], inplace=True)

    # Remplir les valeurs manquantes d'autorité
    df_merged['autorite_delib'] = df_merged['autorite_delib'].fillna("Non spécifié")

    # === Afficher les stats des délibérations ===
    print(f"   ➤ Nombre de parcelles délibérées: {df_merged[df_merged['delibere'] == 'Oui'].shape[0]}")

    # === Colonnes finales à exporter ===
    colonnes_finales = ["id_parcelle", "commune", "Village", "nicad", "superficie", "type_usag", "type_usa", "delibere",
                        "autorite_delib", "Nicad"]
    df_kobo_final = df_kobo_final[[col for col in colonnes_finales if col in df_kobo_final.columns]]
    df_ndoga_final = df_ndoga_final[[col for col in colonnes_finales if col in df_ndoga_final.columns]]

    # Mise à jour avec le résultat de la fusion avec les délibérations
    df_global_final = df_merged[[col for col in colonnes_finales if col in df_merged.columns]]

    # === Export Excel ===
    df_kobo_final.to_excel("parcelles_kobo.xlsx", index=False)
    df_ndoga_final.to_excel("parcelles_ndoga.xlsx", index=False)
    df_global_final.to_excel("parcelles_fusionnées.xlsx", index=False)
    df_global_final[df_global_final["delibere"] == "Oui"].to_excel("parcelles_delibérées.xlsx", index=False)

    # === Résumé ===
    print("\n✅ Export terminé !")
    print(f"   ➤ parcelles_kobo.xlsx : {len(df_kobo_final)} lignes")
    print(f"   ➤ parcelles_ndoga.xlsx : {len(df_ndoga_final)} lignes")
    print(f"   ➤ parcelles_fusionnées.xlsx : {len(df_global_final)} lignes")
    print(f"   ➤ parcelles_delibérées.xlsx : {len(df_global_final[df_global_final['delibere'] == 'Oui'])} lignes")
    print(f"   Répartition NICAD globale :\n{df_global_final['nicad'].value_counts().to_string()}")
    print(f"   Répartition DELIBERE :\n{df_global_final['delibere'].value_counts().to_string()}")

except Exception as e:
    import traceback

    print(f"\n❌ Une erreur est survenue : {e}")
    print(traceback.format_exc())
