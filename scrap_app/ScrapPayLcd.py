from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Configurez le WebDriver
driver = webdriver.Chrome()

url = "https://paylcd.com/fr/rachat"
driver.get(url)

# Attendez que les éléments dynamiques se chargent (peut être ajusté en fonction de la vitesse de chargement)
wait = WebDriverWait(driver, 10)

# Par exemple, attendez que l'élément avec la classe "r_name" apparaisse
element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "r_name")))

# Obtenez le code source de la page après que les données dynamiques aient été chargées
html = driver.page_source

# Fermez le WebDriver
driver.quit()

# Analysez le code HTML à l'aide de BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

# Trouvez tous les éléments qui contiennent le nom et le prix
product_items = soup.find_all('div', class_='ajax_block_product r_product col-xs-12')

# Parcourez les éléments et extrayez le nom et le prix
for item in product_items:
    name_element = item.find('span', {'class': 'r_name'})
    price_element = item.find('span', {'class': 'r_price'})

    if name_element and price_element:
        # Remplacez les virgules par des points dans le nom du modèle
        name = name_element.text.strip().replace(",", ".")

        # Remplacez les virgules par des points dans le prix et supprimez les espaces
        price = price_element['data-price'].replace(',', '.').replace(" ", "")

        # Arrondissez le prix à deux décimales
        price = round(float(price), 2)

        # Ajoutez "PayLcd" au nom
        name = f"PayLcd, {name}"

        # Formatez le prix avec deux décimales
        formatted_price = f"GRADE A, {price:.2f} €"

        # Vérifiez si le nom n'est pas celui que vous ne voulez pas afficher
        if name != "PayLcd, Envoyez. nous trions pour vous !":
            print(f"{name}, {formatted_price}")

