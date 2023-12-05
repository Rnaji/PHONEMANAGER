import os
import subprocess
import csv

def run_scrapers_and_generate_csv(output_csv="scraper_data.csv"):
    scrapers = ["ScrapSmartgrade.py", "Scrapispart.py", "ScrapLcdPhone.py", "ScrapPayLcd.py", "ScrapRecycleMonLcd.py"]
    scraper_directory = "/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app"

    with open(output_csv, mode="w", newline='') as csv_file:
        fieldnames = ["Scraper", "Modèle", "Grade", "Prix"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for scraper in scrapers:
            scraper_path = os.path.join(scraper_directory, scraper)
            process = subprocess.Popen(["python", scraper_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out, err = process.communicate()

            output_lines = out.splitlines()
            for line in output_lines:
                data = line.split(",")  # Adapter cette ligne en fonction du format de sortie de chaque scraper
                cleaned_data = [d.replace('"', '').replace('″', '').replace('é', 'e') for d in data]  # Nettoyer les données

                # Nettoyer et convertir le prix en nombre à virgule flottante avec 2 décimales
                cleaned_price = cleaned_data[3].replace('€', '').strip()  # Nettoyer le symbole '€' et les espaces
                try:
                    prix = round(float(cleaned_price), 2)  # Convertir en flottant avec 2 décimales
                except ValueError:
                    prix = 0  # Remplacer par 0 si la conversion échoue

                cleaned_data[3] = prix  # Remplacer l'ancien prix par le prix nettoyé

                writer.writerow(dict(zip(fieldnames, cleaned_data)))

    print(f"Données des scrapers enregistrées dans {output_csv}")

if __name__ == "__main__":
    run_scrapers_and_generate_csv()
