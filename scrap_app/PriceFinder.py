import json
import pandas as pd

# Charger le fichier correspondances.json
with open("correspondances.json", "r") as f:
    correspondances = json.load(f)

# Charger le fichier CSV
data_ref = pd.read_csv("scraper_data_ref.csv", sep=",")

# Fonction pour trouver les correspondances pour une marque et un modèle donnés
def trouver_correspondances_marque(marque, modele):
    modele = modele.strip()  # Enlever les espaces inutiles

    if marque in correspondances:
        modeles_marque = correspondances[marque]
        if modele in modeles_marque:
            return list(set(modeles_marque[modele]))

    return None

# Saisie utilisateur de la marque
marque_entre = input("Entrez la marque : ")

# Saisie utilisateur du modèle
modele_entre = input("Entrez le modèle : ")

# Saisie utilisateur du grade souhaité (saisie d'une lettre)
grade_saisi = input("Entrez le grade souhaité (A, B, C, D, E, F, G, H, Aftermarket, Fully Broken) : ")

# Assurez-vous que la saisie de l'utilisateur est valide
grades_possibles = ["A", "B", "C", "D", "E", "F", "G", "H", "Aftermarket", "Fully Broken"]
while grade_saisi not in grades_possibles:
    print("Grade invalide. Veuillez entrer un grade valide parmi A, B, C, D, E, F, G, H, Aftermarket, Fully Broken.")
    grade_saisi = input("Entrez le grade souhaité (A, B, C, D, E, F, G, H, Aftermarket, Fully Broken) : ")

# Le reste de votre code reste inchangé.
# Convertir la lettre saisie en "A", "B", "C", ...
grade_demande = grade_saisi

# Trouver les correspondances pour la marque et le modèle donnés
resultat = trouver_correspondances_marque(marque_entre, modele_entre)

# Utiliser un ensemble pour stocker les lignes correspondantes uniques
lignes_correspondantes = set()

if resultat:
    print(f"Correspondances exactes trouvées pour la marque {marque_entre} et le modèle {modele_entre} :")
    print(resultat)

    for modele_trouve in resultat:
        # Rechercher les lignes correspondantes exactes pour chaque modèle trouvé
        lignes_modele = data_ref[data_ref.iloc[:, 1].str.strip().str.lower() == modele_trouve.strip().lower()]

        # Ajouter un filtre pour le grade demandé
        lignes_modele = lignes_modele[lignes_modele.iloc[:, 2].str.strip() == f"grade {grade_demande}"]

        # Convertir chaque ligne (liste) en un tuple avant de l'ajouter à l'ensemble
        lignes_correspondantes.update(map(tuple, lignes_modele.values.tolist()))

    if lignes_correspondantes:
        print(f"Lignes correspondantes exactes avec le grade 'grade {grade_demande}' dans le fichier CSV :")
        lignes_correspondantes = list(lignes_correspondantes)  # Convertir l'ensemble en liste
        lignes_correspondantes = pd.DataFrame(lignes_correspondantes, columns=["Recycler", "Model", "Grade", "Prix"])  # Remplacer les titres des colonnes
        print(lignes_correspondantes)
    else:
        print(f"Aucune ligne correspondante exacte avec le grade 'grade {grade_demande}' trouvée dans le fichier CSV.")
else:
    print(f"Aucun résultat trouvé pour la marque {marque_entre} et le modèle {modele_entre}.")
