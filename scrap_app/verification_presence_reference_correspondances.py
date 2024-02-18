import csv
import json

csv_file_path = '/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/scraper_data_ref.csv'
json_file_path = '/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/correspondances.json'

# Étape 1: Lire le fichier CSV et récupérer la deuxième colonne
unique_values = set()
seen_values = set()  # To keep track of duplicates
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if len(row) >= 2:
            value = row[1].strip()
            if value and value not in seen_values:
                seen_values.add(value)
                unique_values.add(value)

# Étape 2: Lire le fichier JSON
with open(json_file_path, 'r') as json_file:
    correspondances = json.load(json_file)

# Étape 3: Itérer sur les valeurs uniques et afficher celles qui n'apparaissent pas dans le fichier JSON
for marque, modeles in correspondances.items():
    for modele, noms_alternatifs in modeles.items():
        if modele in unique_values:
            unique_values.remove(modele)
        for nom_alternatif in noms_alternatifs:
            if nom_alternatif in unique_values:
                unique_values.remove(nom_alternatif)

# Étape 4: Afficher les valeurs restantes qui n'apparaissent pas dans le fichier JSON
print("Valeurs non trouvées dans le fichier JSON:")
for value in unique_values:
    print(f'"{value}"')
