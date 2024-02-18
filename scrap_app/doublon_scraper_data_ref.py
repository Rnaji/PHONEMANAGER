import pandas as pd

# Charger le fichier CSV dans un DataFrame
df = pd.read_csv('scraper_data_ref.csv')

# Trouver les lignes dupliquées basées sur toutes les colonnes
duplicate_rows = df[df.duplicated()]

# Afficher les lignes dupliquées
print("Lignes dupliquées :")
print(duplicate_rows)
