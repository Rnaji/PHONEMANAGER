# dans votre_app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class StoreConfiguration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    company_name = models.CharField(max_length=100, verbose_name="Dénomination sociale de l'entreprise")
    address = models.TextField(verbose_name="Adresse")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    city = models.CharField(max_length=50, verbose_name="Ville")
    phone_number = models.CharField(max_length=15, verbose_name="Numéro de téléphone")
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Configuration du magasin - {self.company_name}"
