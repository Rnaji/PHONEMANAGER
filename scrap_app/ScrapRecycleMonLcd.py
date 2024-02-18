import requests
from bs4 import BeautifulSoup
import re

url = "https://www.recyclemonlcd.com/"
response = requests.get(url)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    captions = soup.find_all('div', class_='caption')

    processed_models = set()

    for caption in captions:
        model_text = caption.find('div', class_='name').find('a').text.strip()
        cleaned_model = re.sub(r'Rachat écran|original|uniquement|original uniquement', '', model_text)
        cleaned_model = cleaned_model.replace(',', '.')

        unwanted_strings = ["Rachat de telephones et tablettes casses au kilogramme sans batterie",
                            "Rachat d'ecrans full broken et ecrans generiques au kilogramme",
                            "Rachat de cartes mères. connectiques et cameras de smartphones au kilogramme"]

        if cleaned_model not in unwanted_strings:
            price = caption.find('div', class_='price').find('span', class_='price-normal').text.strip()
            price = price.replace(',', '.')

            model_with_recyclemonlcd = f"RecycleMonLcd, {cleaned_model.strip()}"
            price_with_grade_a = f"GRADE A, {price}"

            # Vérifiez si le modèle n'a pas déjà été traité
            if model_with_recyclemonlcd not in processed_models:
                processed_models.add(model_with_recyclemonlcd)
                print(f"{model_with_recyclemonlcd}, {price_with_grade_a}")
