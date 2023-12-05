from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome()

url = "https://ispart.eu/revendre-des-ecrans/"
driver.get(url)

# Wait for the page load (can adjust the time)
import time
time.sleep(5)  # Wait for x seconds

# Extract the HTML content from the page
html = driver.page_source

# Close the WebDriver
driver.quit()

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

# Find all the product items
product_items = soup.find_all("div", class_="product-item")

# Loop through the product items and extract model and price
for item in product_items:
    model = f"ispart, {item.find('h5').text}"  # Ajoute "ispart" au modèle
    price_element = item.find("div", class_="product-item-price")
    price = price_element.text.strip()
    
    # Enlevez le symbole € et formatez le prix avec deux décimales
    price = price.replace('€', '').replace(',', '.')  # Retirez le symbole € et remplacez la virgule par un point
    price = f"GRADE A, {float(price):.2f} €"  # Ajoutez le symbole € et formatez avec deux décimales
    
    print(f"{model}, {price}")

