import csv
import json

csv_file_path = '/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/recycler_updated_price.csv'
json_file_path = '/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/recycler_updated_price.json'

def csv_to_json(csv_file_path, json_file_path):
    data = []

    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            entry = {
                "Marque": row['Marque'],
                "Modèle": row['Modèle'],
                "Grade": row['Grade'],
                "Recycleur": row['Recycleur'],
                "Prix": float(row['Prix']),
            }
            data.append(entry)

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

    print("done")

csv_to_json(csv_file_path, json_file_path)
