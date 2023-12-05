import csv
from collections import defaultdict

def find_duplicate_rows_in_csv_with_price(csv_file):
    rows_seen = defaultdict(list)

    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames

        for row in reader:
            key = tuple(row[column] for column in headers)  # Utiliser toutes les colonnes pour la clé
            rows_seen[key].append(row)

        for key, rows in rows_seen.items():
            if len(rows) > 1:
                print("Lignes identiques :")
                for row in rows:
                    print(row)
                print("----------------------")

if __name__ == "__main__":
    file_path = 'recycler_updated_price.csv'  # Assurez-vous d'indiquer le chemin absolu ou relatif correct
    find_duplicate_rows_in_csv_with_price(file_path)
