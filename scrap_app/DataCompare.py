import os
import subprocess
import csv

# Fonction pour exécuter ScrapAnalyzer et générer le fichier CSV
def run_scrapanalyzer_and_generate_csv(output_csv="scraper_data.csv"):
    # Exécutez ScrapAnalyzer
    subprocess.run(["python", "ScrapAnalyzer.py"], text=True)

# Fonction pour comparer les résultats entre le fichier de référence et le nouveau fichier CSV
def compare_results(reference_csv, new_csv, output_csv):
    with open(reference_csv, 'r') as file_ref, open(new_csv, 'r') as file_new, open(output_csv, 'w', newline='') as file_diff:
        reader_ref = csv.reader(file_ref)
        reader_new = csv.reader(file_new)
        writer_diff = csv.writer(file_diff)

        # Lire l'en-tête (noms de colonnes) des fichiers CSV de référence et de nouveau
        header_ref = next(reader_ref)
        header_new = next(reader_new)

        # Écrire l'en-tête dans le fichier de différences
        writer_diff.writerow(header_ref)

        # Créer un ensemble pour stocker les 3 premières colonnes du fichier de référence
        ref_lines_set = set()

        # Remplir l'ensemble avec les clés (3 premières colonnes) du fichier de référence
        for row_ref in reader_ref:
            key = tuple(row_ref[:3])
            ref_lines_set.add(key)

        # Parcourir les lignes du fichier de nouveau
        for row_new in reader_new:
            key = tuple(row_new[:3])

            # Vérifier si la ligne du fichier de nouveau est dans le fichier de référence
            if key not in ref_lines_set:
                # Si la ligne est absente dans le fichier de référence, écrivez-la dans le fichier de différences
                writer_diff.writerow(row_new)

    print("Comparaison terminée. Les différences ont été enregistrées dans le fichier de différences.")

if __name__ == "__main__":
    reference_csv = "scraper_data_ref.csv"
    new_csv = "scraper_data.csv"
    output_csv = "differences.csv"

    # Exécutez ScrapAnalyzer et générer le fichier CSV
    run_scrapanalyzer_and_generate_csv(new_csv)

    compare_results(reference_csv, new_csv, output_csv)
