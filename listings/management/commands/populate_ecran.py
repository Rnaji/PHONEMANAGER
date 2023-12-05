from django.core.management.base import BaseCommand
from django.db import transaction
from listings.models import ScreenBrand, ScreenModel
import json
from django.http import HttpResponse


class Command(BaseCommand):
    help = 'Peuple la base de données des marques et modèles'

    def handle(self, *args, **options):
        i = 1
        file_path = '/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/screen_modele_data.json'

        try:
            with open(file_path, 'r') as fichier:
                modele_data = json.load(fichier)

                with transaction.atomic():
                    for marque, modeles in modele_data.items():
                        brand, created = ScreenBrand.objects.get_or_create(screenbrand=marque)
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Création de la marque {marque}"))

                        for modele in modeles:
                            model, created = ScreenModel.objects.get_or_create(
                                screenbrand=brand, screenmodel=modele, is_oled=False, is_wanted=False
                            )
                            if created:
                                self.stdout.write(self.style.SUCCESS(f"Création du modèle {modele}"))
                            i += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("Le fichier JSON n'a pas été trouvé."))
            return  # Retourner sans créer une instance d'HttpResponse
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Erreur de décodage du fichier JSON."))
            return  # Retourner sans créer une instance d'HttpResponse
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la création des marques et des modèles : {str(e)}"))
            return  # Retourner sans créer une instance d'HttpResponse

        self.stdout.write(self.style.SUCCESS("Opération réussie"))
