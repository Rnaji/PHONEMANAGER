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

    def __str__(self):
        return self.value



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
        return f"{self.screenmodel}"
    

class Recycler(models.Model):

    company_name = models.CharField(max_length=100, verbose_name="Dénomination sociale de l'entreprise", blank=True)
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
    diag_response_1 = models.BooleanField(null=True)
    diag_response_2 = models.BooleanField(null=True)
    diag_response_3 = models.BooleanField(null=True)
    diag_response_4 = models.BooleanField(null=True)
    diag_response_5 = models.BooleanField(null=True)
    diag_response_6 = models.BooleanField(null=True)
    diag_response_7 = models.BooleanField(null=True)
    diag_response_8 = models.BooleanField(null=True)
    diag_response_9 = models.BooleanField(null=True)
    is_diag_done = models.BooleanField(default=False)
    grade = models.CharField(
        max_length=20,
        choices=[
            ('', 'Select Grade'),
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
            ('E', 'E'),
            ('F', 'F'),
            ('G', 'G'),
            ('Fully Broken', 'Fully Broken'),
            ('Aftermarket', 'Aftermarket')
        ],
        default='EN ATTENTE',
    )
    quotations = models.ManyToManyField('RecyclerPricing', related_name='broken_screens')
    recycler = models.ForeignKey(Recycler, on_delete=models.SET_NULL, null=True, blank=True)
    is_attributed = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_joined']

    def get_matching_recycler_prices(self):
        matching_recycler_prices = self.recycler_prices.filter(
            screenbrand=self.screenbrand,
            screenmodel=self.screenmodel,
            grade=self.grade
        )
        return matching_recycler_prices

    def __str__(self):
        return f"{self.screenbrand} {self.screenmodel} - {self.grade}"

    def get_sorted_recycler_prices(self):
        return self.recycler_prices.all().order_by('price')

    def attribuer_grade_non_oled(self):
        # Extracting responses from the BrokenScreen instance
        question1 = self.diag_response_1
        question2 = self.diag_response_2
        question3 = self.diag_response_3
        question4 = self.diag_response_4
        question5 = self.diag_response_5
        question6 = self.diag_response_6
        question7 = self.diag_response_7
        question8 = self.diag_response_8
        question9 = self.diag_response_9

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == False and
            question5 == False and
            question6 == False and
            question7 == False and
            question8 == False
        ):
            return "A"

        if (
            question1 == False and
            question2 == False and
            question3 == False and
            question4 == False and
            question5 == False and
            question6 == False and
            question7 == False and
            question8 == False
        ):
            return "Aftermarket"

        if (
            question1 == True and
            question2 == False and
            question3 == True and
            question4 == False and
            question5 == False and
            question6 == False and
            question7 == False and
            question8 == False
        ):
            return "B"

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == False and
            question5 == True and
            question6 == False and
            question7 == False and
            question8 == False
        ):
            return "G"

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == False and
            question5 == False and
            question6 == True and
            question7 == False and
            question8 == False
        ):
            return "D"

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == False and
            question5 == False and
            question6 == False and
            question7 == True and
            question8 == True and
            question9 == False
        ):
            return "C"

        if (
            question1 == False or
            question2 == True or
            question3 == True or
            question4 == True or
            question5 == True or
            question6 == True and
            question7 == True and
            question8 == True and
            question9 == True
        ):
            return "Fully Broken"

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == False and
            question5 == False and
            question6 == False and
            question7 == True and
            question8 == True and
            question9 == False
        ):
            return "C"

        return "EN ATTENTE"

    def attribuer_grade_oled(self):
        # Extracting responses from the BrokenScreen instance
        question1 = self.diag_response_1
        question2 = self.diag_response_2
        question3 = self.diag_response_3
        question4 = self.diag_response_4
        question5 = self.diag_response_5
        question6 = self.diag_response_6
        question7 = self.diag_response_7
        question8 = self.diag_response_8


        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == False and
            question6 == False
        ):
            return "A"

        if (
            question1 == False and
            question2 == False and
            question3 == False and
            question4 == False and
            question6 == False
        ):
            return "AFTERMARKET"

        if (
            question1 == True and
            question2 == True and
            question3 == False and
            question4 == False and
            question6 == False
        ):
            return "G"

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == True and
            question5 == False and
            question6 == False
        ):
            return "E"

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == True and
            question5 == True and
            question6 == False
        ):
            return "F"

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == False and
            question6 == True and
            question7 == False and
            question8 == False
        ):
            return "C"

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == False and
            question6 == True and
            question7 == False and
            question8 == True
        ):
            return "D"

        if (
            question1 == True and
            question2 == False and
            question3 == False and
            question4 == False and
            question6 == True and
            question7 == True
        ):
            return "B"
        
        return "EN ATTENTE"

    def save(self, *args, **kwargs):
        if not self.grade:
            if self.some_condition:  # Ajoutez votre propre condition ici si nécessaire
                self.grade = self.attribuer_grade_non_oled()
            else:
                self.grade = self.attribuer_grade_oled()
        super().save(*args, **kwargs)