import requests
from bs4 import BeautifulSoup

# Remplacez "votre_url" par l'URL de la page que vous souhaitez scraper
url = "https://smartgrade.fr/vendre-ecran-casse-smartphone/"

# Effectuez une requête HTTP pour récupérer le contenu HTML de la page
response = requests.get(url)

# Vérifiez si la requête a réussi (code 200 signifie que la page a été récupérée avec succès)
if response.status_code == 200:
    html = response.text
    # Créez un objet Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')

    # Initialisez la variable model_name à l'extérieur de la boucle
    model_name = None

    # Sélectionnez toutes les lignes de tableau (balises <tr>) avec l'attribut data-entry
    rows = soup.find_all('tr', {'data-entry': True})

    # Parcourez les lignes et extrayez les informations de chaque ligne
    for row in rows:
        # Trouvez la balise qui contient le nom du modèle (balise <td> avec l'attribut data-title contenant "Model")
        model_cell = row.find('td', {'data-title': lambda value: 'Model' in value})
        if model_cell:
            model_name = model_cell.find('span', {'class': 'uael-table__text-inner'}).text.strip()

        # Trouvez toutes les cellules de prix (balises <td>) et extrayez les prix
        price_cells = row.find_all('td', {'data-title': True})
        for cell in price_cells:
            grade_name = cell['data-title'].strip()  # Obtenez le nom du grade depuis l'attribut data-title
            price = cell.find('span', {'class': 'uael-table__text-inner'}).text.strip()
            
            # Vérifiez s'il y a le symbole "€" dans le prix avant de l'imprimer
            if "€" in price:
                # Ajoutez "Smartgrade" avant le modèle
                print(f"Smartgrade, {model_name}, {grade_name}, {price}")
else:
    print(f"Échec de la requête HTTP. Statut de réponse : {response.status_code}")
