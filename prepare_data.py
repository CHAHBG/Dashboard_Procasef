import pandas as pd


# === Chargement Excel avec dtypes forcés ===
def charger_fichier(fichier):
    return pd.read_excel(fichier, dtype={'Num_parcel': str, 'Num_parcel_2': str, 'Nicad': str})


# === Harmoniser les noms de colonnes ===
def harmoniser_colonnes(df):
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        'Num_parcel': 'id_parcelle',
        'Num_parcel_2': 'id_parcelle',
        'communeSenegal': 'commune',
        'nicad': 'Nicad'
    })

    if 'Village' not in df.columns:
        df['Village'] = "Non spécifié"

    return df


# === Marquer la correspondance URM (NICAD oui/non) ===
def ajouter_nicad(df_kobo, df_urm):
    df_kobo['id_parcelle'] = df_kobo['id_parcelle'].astype(str)
    df_urm['id_parcelle'] = df_urm['id_parcelle'].astype(str)
    df_kobo["nicad"] = df_kobo["id_parcelle"].isin(df_urm["id_parcelle"]).map({True: "Oui", False: "Non"})
    return df_kobo


# === Ajouter les attributs depuis URM avec fallback sur Kobo ===
def completer_attributs(df_kobo, df_urm, attributs):
    df_urm_subset = df_urm[['id_parcelle'] + [a for a in attributs if a in df_urm.columns]].copy()
    df_merge = df_kobo.merge(df_urm_subset, on='id_parcelle', how='left', suffixes=('', '_urm'))

    for attr in attributs:
        col_urm = f"{attr}_urm"
        if col_urm in df_merge.columns:
            # Priorité à URM, sinon Kobo, sinon "Non spécifié"
            df_merge[attr] = df_merge[col_urm].combine_first(df_merge.get(attr)).fillna("Non spécifié")
            df_merge.drop(columns=[col_urm], inplace=True)
        else:
            # Si pas trouvé dans URM, prendre Kobo ou remplir
            df_merge[attr] = df_merge.get(attr, "Non spécifié").fillna("Non spécifié")

    return df_merge


# === Chemins des fichiers ===
kobo_individuels = charger_fichier(r"C:\Users\ASUS\Downloads\Enquete_Foncière-Parcelles_Individuelles_29042025.xlsx")
kobo_collectifs = charger_fichier(r"C:\Users\ASUS\Downloads\Enquete_Foncière-Parcelles_Collectives_29042025.xlsx")
urm_individuels = charger_fichier(
    r"C:\Users\ASUS\Downloads\3.a Validation par URM\3.a Validation par URM\All NICADS\GPKG Merged\parcelles_individuelles_nicad_Lot5_32.xlsx")
urm_collectifs = charger_fichier(
    r"C:\Users\ASUS\Downloads\3.a Validation par URM\3.a Validation par URM\All NICADS\GPKG Merged\parcelles_collectives_nicad_Lot5_32.xlsx")

# === Harmonisation des colonnes ===
df_kobo_ind = harmoniser_colonnes(kobo_individuels)
df_kobo_col = harmoniser_colonnes(kobo_collectifs)
df_urm_ind = harmoniser_colonnes(urm_individuels)
df_urm_col = harmoniser_colonnes(urm_collectifs)

try:
    print("🔍 Traitement des parcelles individuelles...")
    df_kobo_ind = ajouter_nicad(df_kobo_ind, df_urm_ind)
    df_kobo_ind = completer_attributs(df_kobo_ind, df_urm_ind, ['superficie', 'type_usag'])

    # Champ type_usa non applicable pour les individuels
    df_kobo_ind['type_usa'] = "Non applicable"

    print("🔍 Traitement des parcelles collectives...")
    df_kobo_col = ajouter_nicad(df_kobo_col, df_urm_col)
    df_kobo_col = completer_attributs(df_kobo_col, df_urm_col, ['superficie', 'type_usa'])

    # Champ type_usag non applicable pour les collectifs
    df_kobo_col['type_usag'] = "Non applicable"

    # === Fusion finale ===
    df_final = pd.concat([df_kobo_ind, df_kobo_col], ignore_index=True)

    colonnes_finales = ["id_parcelle", "commune", "Village", "nicad", "superficie", "type_usag", "type_usa"]
    df_final = df_final[[col for col in colonnes_finales if col in df_final.columns]]

    # === Export Excel ===
    df_final.to_excel("parcelles.xlsx", index=False)

    print("\n✅ Fichier 'parcelles.xlsx' généré avec succès !")
    print(f"   Nombre total de lignes : {len(df_final)}")
    print(f"   Répartition NICAD :\n{df_final['nicad'].value_counts().to_string()}")
    print("   Colonnes principales : superficie, type_usag, type_usa (priorité URM, sinon Kobo)")

except Exception as e:
    print(f"\n❌ Une erreur est survenue : {e}")
