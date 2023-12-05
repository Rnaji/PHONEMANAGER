import requests
from bs4 import BeautifulSoup

# Remplacez l'URL par l'URL de la page que vous souhaitez scraper
url = 'https://lcd-phone.com/fr/content/8-rachat-et-recyclage-ecran-casse'

# Effectuez une requête HTTP pour obtenir le contenu de la page
response = requests.get(url)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # Extraction de données pour la première table (iPhones)
    table = soup.find('table')

    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        if len(columns) == 4:
            modele = columns[0].text.strip().replace("Modèle, ", "")
            prix_a = columns[1].text.strip().replace("Prix Class A, ", "").replace(',', '.').strip()
            prix_b = columns[2].text.strip().replace("Prix Class B, ", "").replace(',', '.').strip()

            # Supprimez la ligne "Prix de reconditionnement" et affichez les données sur une seule ligne avec "LcdPhone"
            print(f"LcdPhone, {modele}, GRADE A, {prix_a}")
            print(f"LcdPhone, {modele}, GRADE B, {prix_b}")


    # Extraction de données pour la table des iPads (Supposons que c'est la deuxième table)
    ipad_table = soup.find_all('table')[1]

    for row in ipad_table.find_all('tr')[2:]:
        columns = row.find_all('td')
        if len(columns) == 3:
            modele = columns[0].text.strip().replace("Modèle: ", "")
            prix_a = columns[1].text.strip().replace("Prix Class A, ", "").replace(',', '.').strip()
            prix_b = columns[2].text.strip().replace("Prix Class B, ", "").replace(',', '.').strip()

            # Supprimez la ligne "Prix de reconditionnement" et affichez les données sur une seule ligne avec "LcdPhone"
            print(f"LcdPhone, {modele}, GRADE A, {prix_a}")
            print(f"LcdPhone, {modele}, GRADE B, {prix_b}")


    # Recherche de la balise <h2> contenant "Samsung Galaxy S"
    samsung_header = soup.find('h2', string="Samsung Galaxy S")
    if samsung_header:
        samsung_table = samsung_header.find_next('table')

        for row in samsung_table.find_all('tr')[1:]:
            columns = row.find_all('td')
            if len(columns) == 6:
                modele = columns[0].text.strip().replace("Modèle: ", "")
                prix_a = columns[1].text.strip().replace("Prix Class A, ", "").replace(',', '.').strip() + " €"
                prix_b = columns[2].text.strip().replace("Prix Class B, ", "").replace(',', '.').strip() + " €"
                prix_c = columns[3].text.strip().replace("Prix Class C, ", "").replace(',', '.').strip() + " €"
                prix_d = columns[4].text.strip().replace("Prix Class D, ", "").replace(',', '.').strip() + " €"

                # Supprimez la ligne "Prix de reconditionnement" et affichez les données sur une seule ligne avec "LcdPhone"
                print(f"LcdPhone, {modele}, GRADE A, {prix_a}")
                print(f"LcdPhone, {modele}, GRADE B, {prix_b}")
                print(f"LcdPhone, {modele}, GRADE C, {prix_c}")
                print(f"LcdPhone, {modele}, GRADE D, {prix_d}")


    else:
        print("Balise 'Samsung Galaxy S' non trouvée.")
else:
    print(f"La requête à l'URL {url} a échoué avec le code d'état {response.status_code}")

samsung_note_header = soup.find('h2', string="Samsung Galaxy Note")
if samsung_note_header:
    samsung_note_table = samsung_note_header.find_next('table')

    for row in samsung_note_table.find_all('tr')[1:]:
        columns = row.find_all('td')
        if len(columns) == 6:
            modele = columns[0].text.strip().replace("Modèle, ", "")
            prix_a = columns[1].text.strip().replace("Prix Class A, ", "").replace(',', '.').strip() + " €"
            prix_b = columns[2].text.strip().replace("Prix Class B, ", "").replace(',', '.').strip() + " €"
            prix_c = columns[3].text.strip().replace("Prix Class C, ", "").replace(',', '.').strip() + " €"
            prix_d = columns[4].text.strip().replace("Prix Class D, ", "").replace(',', '.').strip() + " €"

            # Supprimez la ligne "Prix de reconditionnement" et affichez les données sur une seule ligne avec "LcdPhone"
            print(f"LcdPhone, {modele}, GRADE A, {prix_a}")
            print(f"LcdPhone, {modele}, GRADE B, {prix_b}")
            print(f"LcdPhone, {modele}, GRADE C, {prix_c}")
            print(f"LcdPhone, {modele}, GRADE D, {prix_d}")

else:
    print("Balise 'Samsung Galaxy Note' non trouvée.")

# Recherche de la balise <h2> contenant "Samsung Galaxy A / J"
samsung_aj_header = soup.find('h2', string="Samsung Galaxy A / J")
if samsung_aj_header:
    samsung_aj_table = samsung_aj_header.find_next('table')

    for row in samsung_aj_table.find_all('tr')[1:]:
        columns = row.find_all('td')
        if len(columns) == 4:
            modele = columns[0].text.strip().replace("Modèle: ", "")
            prix_a = columns[1].text.strip().replace("Prix Class A, ", "").replace(',', '.').strip() + " €"
            prix_b = columns[2].text.strip().replace("Prix Class B, ", "").replace(',', '.').strip() + " €"
