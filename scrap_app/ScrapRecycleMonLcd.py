import requests
from bs4 import BeautifulSoup
import re

# Remplacez "votre_url" par l'URL de la page que vous souhaitez scraper
url = "https://www.recyclemonlcd.com/"

# Effectuez une requête HTTP pour récupérer le contenu HTML de la page
response = requests.get(url)

# Vérifiez si la requête a réussi (code 200 signifie que la page a été récupérée avec succès)
if response.status_code == 200:
    html = response.text
    # Créez un objet Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')

    # Sélectionnez tous les éléments "caption" contenant les informations sur les modèles et les prix
    captions = soup.find_all('div', class_='caption')

    for caption in captions:
        # Extrait le modèle complet
        model_text = caption.find('div', class_='name').find('a').text.strip()

        # Utilise une expression régulière pour enlever "Rachat écran" et "original uniquement"
        cleaned_model = re.sub(r'Rachat écran|original|uniquement|original uniquement', '', model_text)

        # Remplacez les virgules par des points dans le nom du modèle
        cleaned_model = cleaned_model.replace(',', '.')

        # Extrait le prix et remplace la virgule par un point
        price = caption.find('div', class_='price').find('span', class_='price-normal').text.strip()
        price = price.replace(',', '.')

        # Ajoute "RecycleMonLcd" au modèle
        model_with_recyclemonlcd = f"RecycleMonLcd, {cleaned_model.strip()}"

        # Ajoute "GRADE A" avant le prix
        price_with_grade_a = f"GRADE A, {price}"

        # Imprime le modèle nettoyé avec "RecycleMonLcd", "GRADE A" et le prix sur la même ligne
        print(f"{model_with_recyclemonlcd}, {price_with_grade_a}")
else:
    print(f"Échec de la requête HTTP. Statut de réponse : {response.status_code}")
