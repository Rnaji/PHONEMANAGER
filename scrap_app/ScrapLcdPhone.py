import requests
from bs4 import BeautifulSoup

url = 'https://lcd-phone.com/fr/content/8-rachat-et-recyclage-ecran-casse'
response = requests.get(url)

if response.status_code == 200:
    html_text = response.text
    soup = BeautifulSoup(html_text, 'html.parser')

    models_data = []

    # Chercher toutes les lignes de la table
    for row in soup.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) >= 3:
            model = columns[0].get_text(strip=True).lower()

            # Ignorer les lignes indésirables
            if model in ['modèle', '', 'grade a', 'grade b', 'grade c', 'grade d',
                         'lcd pas de défaut', 'lcd ombre rouge léger', 'lcd ombre rouge visible',
                         'lcd ombre rouge grave']:
                continue

            grade_a = columns[1].get_text(strip=True).replace('€', '').replace(' ', '').replace(',', '.')
            grade_b = columns[2].get_text(strip=True).replace('€', '').replace(' ', '').replace(',', '.')

            # Ajoutez une condition pour le format des prix
            if grade_a.replace('.', '', 1).isdigit():
                grade_a = "{:.2f}".format(float(grade_a))
            if grade_b.replace('.', '', 1).isdigit():
                grade_b = "{:.2f}".format(float(grade_b))

            if "iphone" in model:
                # Si le modèle est un iPhone, n'incluez pas la troisième colonne
                models_data.append({
                    "Model": model,
                    "Grade A": grade_a,
                    "Grade B": grade_b
                })
            elif len(columns) == 4:
                grade_g = columns[3].get_text(strip=True).replace('€', '').replace(' ', '').replace(',', '.')
                # Ajoutez une condition pour le format des prix
                if grade_g.replace('.', '', 1).isdigit():
                    grade_g = "{:.2f}".format(float(grade_g))

                models_data.append({
                    "Model": model,
                    "Grade A": grade_a,
                    "Grade B": grade_b,
                    "Grade G": grade_g
                })

    for data in models_data:
        model_name = "LcdPhone, " + data["Model"]
        for grade, value in data.items():
            if grade != "Model" and value != '':
                print(f"{model_name}, {grade}, {value}€")

else:
    print(f"Échec de la requête avec le code d'état {response.status_code}")
