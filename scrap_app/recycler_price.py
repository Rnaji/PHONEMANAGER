import json
import pandas as pd

# Charger le fichier correspondances.json
with open("correspondances.json", "r") as f:
    correspondances = json.load(f)

# Charger le fichier CSV
data_ref = pd.read_csv("scraper_data_ref.csv", sep=",")

# Charger les données de marques et modèles à partir du fichier JSON
with open("screen_modele_data.json", "r") as json_file:
    data = json.load(json_file)

# Extraire les listes de marques et de modèles du JSON
marques_possibles = list(data.keys())
modeles_possibles = [modele for marque in marques_possibles for modele in data[marque]]

# Définir les valeurs possibles pour le grade et le recycleur
grades_possibles = ["A", "B", "C", "D", "E", "F", "G", "H", "Aftermarket", "Fully Broken"]
recycleurs_possibles = ["ispart", "smartgrade", "lcdphone", "paylcd", "recyclemonlcd"]

# Créer une liste pour stocker les résultats
resultats = []

# Modifier la fonction pour trouver les correspondances pour une marque et un modèle donnés
def trouver_correspondances_marque(marque, modele):
    modele = modele.strip()  # Enlever les espaces inutiles

    if marque in correspondances:
        modeles_marque = correspondances[marque]
        if modele in modeles_marque:
            # Si le modèle est trouvé, récupérer directement les correspondances sans préfixe "Grade"
            resultats_sans_prefixe = [elem for elem in modeles_marque[modele] if not elem.startswith("Grade")]
            return list(set(resultats_sans_prefixe))

    return None

for marque in marques_possibles:
    for modele in data[marque]:
        for grade in grades_possibles:
            for recycleur in recycleurs_possibles:
                print(f"Marque: {marque}, Modèle: {modele}, Grade: {grade}, Recycleur: {recycleur}")

                resultat = trouver_correspondances_marque(marque, modele)

                if resultat:
                    for modele_trouve in resultat:
                        lignes_modele = data_ref[data_ref.iloc[:, 1].str.strip().str.lower() == modele_trouve.strip().lower()]

                        print("Lignes avant filtrage :")
                        print(lignes_modele)  # Afficher les lignes avant le filtrage

                        lignes_modele = lignes_modele[
                            ((lignes_modele.iloc[:, 2].str.strip().str.lower() == grade.lower()) |
                             (lignes_modele.iloc[:, 2].str.strip().str.lower() == f"grade {grade.lower()}")) &
                            (lignes_modele.iloc[:, 0].str.lower() == recycleur)
                        ]

                        print("Lignes après filtrage :")
                        print(lignes_modele)  # Afficher les lignes après le filtrage

                        if not lignes_modele.empty:
                            prix = lignes_modele.iloc[0, 3]  # Utiliser la quatrième colonne pour le prix
                            recycleur_trouve = lignes_modele.iloc[0, 0]  # Utiliser la première colonne pour le nom du recycleur

                            resultats.append({
                                "Marque": marque,
                                "Modèle": modele,
                                "Grade": grade,
                                "Recycleur": recycleur,
                                "Prix": prix
                            })

print(resultats)

df = pd.DataFrame(resultats)

df.to_csv("recycler_updated_price.csv", index=False)

with open("recycler_updated_price.json", "w", encoding='utf-8') as json_file:
    json.dump(resultats, json_file, indent=4, ensure_ascii=False)

print("Les résultats ont été enregistrés dans les fichiers recycler_updated_price.csv et recycler_updated_price.json.")
