from django.core.management.base import BaseCommand
from django.db import transaction
from listings.models import ScreenModel, Recycler, RecyclerPricing
import json
from django.http import HttpResponse

class Command(BaseCommand):
    help = 'Peuple la base de données avec les prix de recyclage'

    def handle(self, *args, **options):
        file_path = '/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/recycler_updated_price.json'

        try:
            # Récupérer le recycleur existant ou le créer s'il n'existe pas
            recycleur, created = Recycler.objects.get_or_create(company_name="Votrerecycleur")

            # Parcourir toutes les combinaisons possibles de screenbrand, screenmodel et grade
            for modele_ecran in ScreenModel.objects.all():
                for grade, _ in RecyclerPricing._meta.get_field('grade').choices:

                    # Vérifier si le prix existe déjà, sinon le créer
                    prix_recycleur, created = RecyclerPricing.objects.update_or_create(
                        recycler=recycleur,
                        screenbrand=modele_ecran.screenbrand,
                        screenmodel=modele_ecran,
                        grade=grade,
                        defaults={'price': 0}
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(
                            f"Prix créé pour {modele_ecran.screenbrand.screenbrand} {modele_ecran.screenmodel} ({grade}) chez {recycleur.company_name} : 0"
                        ))
                    else:
                        self.stdout.write(self.style.SUCCESS(
                            f"Prix mis à jour pour {modele_ecran.screenbrand.screenbrand} {modele_ecran.screenmodel} ({grade}) chez {recycleur.company_name} : 0"
                        ))

            # Lire les données JSON
            with open(file_path, 'r') as fichier:
                donnees_prix = json.load(fichier)

               # ...

            # Traiter les données JSON
            with transaction.atomic():
                for item in donnees_prix:
                    nom_marque = item["Marque"]
                    nom_modele = item["Modèle"]
                    grade = item["Grade"]
                    recycleur_name = item["Recycleur"]

                    prix_value = item["Prix"]
                    prix = float(prix_value.replace(' €', '')) if isinstance(prix_value, str) else float(prix_value)

                    print(f"Processing: {nom_marque} {nom_modele} ({grade}) chez {recycleur_name} : {prix}")

                    try:
                        modele_ecran = ScreenModel.objects.get(
                            screenbrand__screenbrand=nom_marque, screenmodel=nom_modele
                        )
                        print(f"Modèle {nom_marque} {nom_modele} trouvé.")
                    except ScreenModel.DoesNotExist:
                        print(f"Modèle {nom_marque} {nom_modele} non trouvé.")
                        continue
                    except ScreenModel.MultipleObjectsReturned:
                        print(f"Plusieurs modèles trouvés pour {nom_marque} {nom_modele}. Veuillez ajuster les données.")
                        continue

                    # Récupérer le recycleur existant ou le créer s'il n'existe pas
                    recycleur, created = Recycler.objects.get_or_create(company_name=recycleur_name)

                    # Mettre à jour ou créer le prix de recyclage
                    prix_recycleur, created = RecyclerPricing.objects.update_or_create(
                        recycler=recycleur,
                        screenbrand=modele_ecran.screenbrand,
                        screenmodel=modele_ecran,
                        grade=grade,
                        defaults={'price': prix}
                    )

                    if created:
                        print(f"Prix créé pour {nom_marque} {nom_modele} ({grade}) chez {recycleur_name} : {prix}")
                    else:
                        print(f"Prix mis à jour pour {nom_marque} {nom_modele} ({grade}) chez {recycleur_name} : {prix}")

            # ...


        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("Le fichier JSON n'a pas été trouvé."))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Erreur de décodage du fichier JSON."))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Une erreur s'est produite : {str(e)}"))
            return

        self.stdout.write(self.style.SUCCESS("Opération réussie"))
