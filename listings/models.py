# listings/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string
import random

class RepairStore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    company_name = models.CharField(max_length=100, verbose_name="Dénomination sociale de l'entreprise")
    address = models.TextField(verbose_name="Adresse")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    city = models.CharField(max_length=50, verbose_name="Ville")
    phone_number = models.CharField(max_length=15, verbose_name="Numéro de téléphone")
    date_joined = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return f"Configuration du magasin - {self.company_name}"

    def get_unused_ref_unique_list(self):
        current_references_count = UniqueReference.objects.filter(repairstore=self, is_used=False).count()
        references_to_generate = 65 - current_references_count

        for _ in range(references_to_generate):
            self.create_new_unique_reference()

        return UniqueReference.objects.filter(repairstore=self, is_used=False)

    def create_new_unique_reference(self):
        while True:
            new_reference_value = UniqueReference.generate_unique_reference_value()

            if not UniqueReference.objects.filter(value=new_reference_value).exists():
                UniqueReference.objects.create(repairstore=self, value=new_reference_value)
                break

class UniqueReference(models.Model):
    repairstore = models.ForeignKey(RepairStore, on_delete=models.CASCADE)
    value = models.CharField(max_length=6, unique=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def get_unused_unique_reference(cls):
        try:
            return cls.objects.filter(is_used=False).first()
        except cls.DoesNotExist:
            return None

    def mark_as_used(self):
        self.is_used = True
        self.save()

    @classmethod
    def generate_unique_reference_value(cls):
        characters = string.ascii_letters + string.digits
        unique_value = ''.join(random.choice(characters) for _ in range(6))
        return unique_value




class ScreenBrand(models.Model):
    screenbrand = models.CharField(max_length=25, primary_key=True, null=False, blank=False)

    class Meta:
        ordering = ['screenbrand']

    def __str__(self):
        return self.screenbrand

class ScreenModel(models.Model):
    screenbrand = models.ForeignKey(ScreenBrand, on_delete=models.CASCADE)
    screenmodel = models.CharField(max_length=50)
    is_oled = models.BooleanField(default=False)
    is_wanted = models.BooleanField(default=False)

    class Meta:
        ordering = ['screenbrand', 'screenmodel']

    def __str__(self):
        return f"{self.screenbrand} {self.screenmodel}"
    

class Recycler(models.Model):

    company_name = models.CharField(max_length=100, verbose_name="Dénomination sociale de l'entreprise")
    address = models.TextField(verbose_name="Adresse")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    city = models.CharField(max_length=50, verbose_name="Ville")
    phone_number = models.CharField(max_length=15, verbose_name="Numéro de téléphone")
    date_joined = models.DateTimeField(default=timezone.now, blank=True, null=True)
    is_us = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name
    

from django.db import models
from .models import Recycler, ScreenModel

class RecyclerPricing(models.Model):
    recycler = models.ForeignKey(Recycler, on_delete=models.CASCADE)
    screenbrand = models.ForeignKey(ScreenBrand, on_delete=models.CASCADE)
    screenmodel = models.ForeignKey(ScreenModel, on_delete=models.CASCADE)
    grade = models.CharField(max_length=20, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G'),
        ('Fully Broken', 'Fully Broken'),
        ('Aftermarket', 'Aftermarket')
    ])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['recycler', 'screenbrand', 'screenmodel', 'grade']

    def __str__(self):
        return f"Prix de {self.recycler.company_name} pour {self.screenbrand} {self.screenmodel} - {self.grade}"


class BrokenScreen(models.Model):
    repairstore = models.ForeignKey(RepairStore, on_delete=models.CASCADE)
    uniquereference = models.OneToOneField(UniqueReference, on_delete=models.CASCADE)
    screenbrand = models.ForeignKey(ScreenBrand, on_delete=models.CASCADE)
    screenmodel = models.ForeignKey(ScreenModel, on_delete=models.CASCADE)
    recycler_prices = models.ManyToManyField(RecyclerPricing, related_name='broken_screens')
    is_attributed = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"Écran cassé - {self.screenbrand} {self.screenmodel} - {self.repairstore}"

    def get_sorted_recycler_prices(self):
        return self.recycler_prices.all().order_by('price')
