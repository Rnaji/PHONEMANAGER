# listings/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string
import random
from django.db.models import Sum
import logging
from django.http import Http404


logger = logging.getLogger(__name__)



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
        characters = string.ascii_uppercase.replace('O', '') + string.digits.replace('0', '')  # Exclure la lettre 'O'
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
    is_3dtouch = models.BooleanField(default=False)
    is_wanted = models.BooleanField(default=False)

    class Meta:
        ordering = ['screenbrand', 'screenmodel']

    def __str__(self):
        return f"{self.screenmodel}"
    

class Recycler(models.Model):

    company_name = models.CharField(max_length=100, verbose_name="Dénomination sociale de l'entreprise", blank=True)
    company_raison_social = models.CharField(max_length=100, verbose_name="Raison sociale", blank=True)
    siren = models.CharField(max_length=15, verbose_name="Numéro siren")
    address = models.TextField(verbose_name="Adresse")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    city = models.CharField(max_length=50, verbose_name="Ville")
    phone_number = models.CharField(max_length=15, verbose_name="Numéro de téléphone")
    url = models.URLField()
    payment_method = models.CharField(max_length=50)
    payment_delay = models.TextField(blank=True, null=True)
    shipping_fee = models.CharField(max_length=50)
    date_joined = models.DateTimeField(default=timezone.now, blank=True, null=True)
    is_us = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name
    

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
    id = models.AutoField(primary_key=True)
    repairstore = models.ForeignKey(RepairStore, on_delete=models.CASCADE)
    uniquereference = models.OneToOneField(UniqueReference, on_delete=models.CASCADE)
    screenbrand = models.ForeignKey(ScreenBrand, on_delete=models.CASCADE)
    screenmodel = models.ForeignKey(ScreenModel, on_delete=models.CASCADE)
    diag_question_1 = models.TextField(null=True, blank=True)
    diag_question_2 = models.TextField(null=True, blank=True)
    diag_question_3 = models.TextField(null=True, blank=True)
    diag_question_4 = models.TextField(null=True, blank=True)
    diag_question_5 = models.TextField(null=True, blank=True)
    diag_question_6 = models.TextField(null=True, blank=True)
    diag_question_7 = models.TextField(null=True, blank=True)
    diag_question_8 = models.TextField(null=True, blank=True)
    diag_question_9 = models.TextField(null=True, blank=True)
    diag_question_10 = models.TextField(null=True, blank=True)
    diag_response_1 = models.BooleanField(null=True)
    diag_response_2 = models.BooleanField(null=True)
    diag_response_3 = models.BooleanField(null=True)
    diag_response_4 = models.BooleanField(null=True)
    diag_response_5 = models.BooleanField(null=True)
    diag_response_6 = models.BooleanField(null=True)
    diag_response_7 = models.BooleanField(null=True)
    diag_response_8 = models.BooleanField(null=True)
    diag_response_9 = models.BooleanField(null=True)
    diag_response_10 = models.BooleanField(null=True)

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
    is_packed = models.BooleanField(default=False)
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
    
    def mark_as_attributed(self):
        self.is_attributed = True
        self.save()

    def mark_as_shipped(self):
        self.is_shipped = True
        self.save()

    def __str__(self):
        return f"{self.screenbrand} {self.screenmodel} - {self.grade}"

    def get_sorted_recycler_prices(self):
        return self.recycler_prices.all().order_by('price')

    def attribuer_grade_oled_apple(self):
        # Extracting responses from the BrokenScreen instance
        question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 = (
            self.diag_response_1, self.diag_response_2, self.diag_response_3,
            self.diag_response_4, self.diag_response_5, self.diag_response_6,
            self.diag_response_7, self.diag_response_8, self.diag_response_9, self.diag_response_10
        )

        # Remplacer les valeurs None par False
        responses = [question1, question2, question3, question4, question5, question6, question7, question8, question9, question10]
        responses = [False if response is None else response for response in responses]

        # Votre logique spécifique avec les réponses individuelles pour le grade A
        if all(
            response == expected_response
            for response, expected_response in zip(responses, [True, False, False, False, False, False, False, False])
        ):
            return "A"

        # Votre logique spécifique avec les réponses individuelles pour le grade B
        elif (
            responses[0] == True and
            responses[1] == False and
            responses[2] == False and
            responses[3] == False and
            responses[4] == False and
            responses[5] == True and
            responses[6] == True and
            responses[7] == False
        ):
            return "B"
        
        elif (
            responses[0] == True and
            responses[1] == False and
            responses[2] == False and
            responses[3] == False and
            responses[4] == False and
            responses[5] == True and
            responses[6] == False and
            responses[7] == False
        ):
            return "C"
        
        elif (
            responses[0] == True and
            responses[1] == False and
            responses[2] == False and
            responses[3] == False and
            responses[4] == False and
            responses[5] == True and
            responses[6] == False and
            responses[7] == True
        ):
            return "D"
        
        elif (
            responses[0] == True and
            responses[1] == False and
            responses[2] == True and
            responses[3] == False and
            responses[4] == False and
            responses[5] == False and
            responses[6] == False and
            responses[7] == False
        ):
            return "G"

        elif (
                responses[0] == False and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False 
            ):
                return "Aftermarket"
        
        return "Fully Broken"



    
    def attribuer_grade_not_oled_apple(self):
        # Extracting responses from the BrokenScreen instance
        question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 = (
            self.diag_response_1, self.diag_response_2, self.diag_response_3,
            self.diag_response_4, self.diag_response_5, self.diag_response_6,
            self.diag_response_7, self.diag_response_8, self.diag_response_9, self.diag_response_10
        )

        # Remplacer les valeurs None par False
        responses = [question1, question2, question3, question4, question5, question6, question7, question8, question9, question10]
        responses = [False if response is None else response for response in responses]

        # Votre logique spécifique avec les réponses individuelles pour le grade A
        if all(
            response == expected_response
            for response, expected_response in zip(responses, [True, False, False, False, False, False, False, False, False])
        ):
            return "A"
        
        # Votre logique spécifique avec les réponses individuelles pour le grade B
        elif (
            responses[0] == True and
            responses[1] == False and
            (responses[2] == True or responses[3] == True or responses[7] == True) and
            responses[4] == False and
            responses[5] == False and
            responses[6] == False and
            responses[8] == False

        ):
            return "B"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                (responses[5] == True or (responses[7] == True and responses[8] == True)) and
                responses[6] == False
            ):
                return "C"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == True and
                responses[6] == True and
                responses[7] == False and
                responses[8] == False
            ):
                return "D"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == True and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "G"
        
        elif (
                responses[0] == False and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "Aftermarket"
        
        return "Fully Broken"
        


    
    def attribuer_grade_oled_apple_3dt(self):
    # Extracting responses from the BrokenScreen instance
        question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 = (
            self.diag_response_1, self.diag_response_2, self.diag_response_3,
            self.diag_response_4, self.diag_response_5, self.diag_response_6,
            self.diag_response_7, self.diag_response_8, self.diag_response_9, self.diag_response_10
        )

        # Remplacer les valeurs None par False
        responses = [question1, question2, question3, question4, question5, question6, question7, question8, question9, question10]
        responses = [False if response is None else response for response in responses]

        # Votre logique spécifique avec les réponses individuelles pour le grade A
        if all(
            response == expected_response
            for response, expected_response in zip(responses, [True, False, False, False, False, False, False, False])
        ):
            return "A"

        # Votre logique spécifique avec les réponses individuelles pour le grade B
        elif (
            responses[0] == True and
            responses[1] == False and
            responses[2] == False and
            responses[3] == False and
            responses[4] == False and
            responses[5] == True and
            responses[6] == True and
            responses[7] == False
        ):
            return "B"
        
        # Votre logique spécifique avec les réponses individuelles pour le grade C
        elif (
            responses[0] == True and
            responses[1] == False and
            responses[2] == False and
            responses[3] == False and
            responses[4] == False and
            responses[5] == True and
            responses[6] == False and
            responses[7] == False
        ):
            return "C"
        
        # Votre logique spécifique avec les réponses individuelles pour les deux conditions du grade D
        elif (
            responses[0] == True and
            responses[1] == False and
            responses[2] == False and
            (responses[3] == True or (responses[6] == True and responses[7] == False and responses[8] == True)) and
            responses[4] == False and
            responses[5] == False

        ):
            return "D"
        
        
        # Votre logique spécifique avec les réponses individuelles pour le grade G
        elif (
            responses[0] == True and
            responses[1] == False and
            responses[2] == True and
            responses[3] == False and
            responses[4] == False and
            responses[5] == False and
            responses[6] == False and
            responses[7] == False
        ):
            return "G"

        elif (
                responses[0] == False and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "Aftermarket"
        
        return "Fully Broken"
    
    def attribuer_grade_not_oled_apple_3dt(self):
         # Extracting responses from the BrokenScreen instance
        question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 = (
            self.diag_response_1, self.diag_response_2, self.diag_response_3,
            self.diag_response_4, self.diag_response_5, self.diag_response_6,
            self.diag_response_7, self.diag_response_8, self.diag_response_9, self.diag_response_10
        )

        # Remplacer les valeurs None par False
        responses = [question1, question2, question3, question4, question5, question6, question7, question8, question9, question10]
        responses = [False if response is None else response for response in responses]

        # Votre logique spécifique avec les réponses individuelles pour le grade A
        if all(
            response == expected_response
            for response, expected_response in zip(responses, [True, False, False, False, False, False, False, False, False, False])
        ):
            return "A"
        
        # Votre logique spécifique avec les réponses individuelles pour le grade B
        elif (
            responses[0] == True and
            responses[1] == False and
            (responses[2] == True or responses[3] == True or responses[8] == True) and
            responses[4] == False and
            responses[5] == False and
            responses[6] == False and
            responses[7] == False and
            responses[9] == False

        ):
            return "B"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                (responses[6] == True or (responses[8] == True and responses[9] == True)) and
                responses[7] == False
            ):
                return "C"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                (responses[5] == True or (responses[6] == True and responses[7] == True)) and
                responses[8] == False and
                responses[9] == False

            ):
                return "D"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == True and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "G"
        
        elif (
                responses[0] == False and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "Aftermarket"
        
        return "Fully Broken"
    
    def attribuer_grade_general_oled(self):
        # Extracting responses from the BrokenScreen instance
        question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 = (
            self.diag_response_1, self.diag_response_2, self.diag_response_3,
            self.diag_response_4, self.diag_response_5, self.diag_response_6,
            self.diag_response_7, self.diag_response_8, self.diag_response_9, self.diag_response_10
        )

        # Remplacer les valeurs None par False
        responses = [question1, question2, question3, question4, question5, question6, question7, question8, question9, question10]
        responses = [False if response is None else response for response in responses]

        # Votre logique spécifique avec les réponses individuelles pour le grade A
        if all(
            response == expected_response
            for response, expected_response in zip(responses, [True, False, False, False, False, False, False, False, False])
        ):
            return "A"
        
        # Votre logique spécifique avec les réponses individuelles pour le grade B
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == True and
                responses[7] == True and
                responses[8] == False
            ):
                return "B"
        
        # Votre logique spécifique avec les réponses individuelles pour le grade C
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == True and
                responses[7] == False and
                responses[8] == False
            ):
                return "C"
        
        # Votre logique spécifique avec les réponses individuelles pour le grade D
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == True and
                responses[7] == False and
                responses[8] == True
            ):
                return "D"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == True and
                responses[4] == True and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "E"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == True and
                responses[4] == False and
                responses[5] == True and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "F"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == True and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "G"
        elif (
                responses[0] == False and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "Aftermarket"
        
        return "Fully Broken"




    def attribuer_grade_general_not_oled(self):
        # Extracting responses from the BrokenScreen instance
        question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 = (
            self.diag_response_1, self.diag_response_2, self.diag_response_3,
            self.diag_response_4, self.diag_response_5, self.diag_response_6,
            self.diag_response_7, self.diag_response_8, self.diag_response_9, self.diag_response_10
        )

        # Remplacer les valeurs None par False
        responses = [question1, question2, question3, question4, question5, question6, question7, question8, question9, question10]
        responses = [False if response is None else response for response in responses]

        # Votre logique spécifique avec les réponses individuelles pour le grade A
        if all(
            response == expected_response
            for response, expected_response in zip(responses, [True, False, False, False, False, False, False, False, False])
        ):
            return "A"
        
        # Votre logique spécifique avec les réponses individuelles pour le grade B
        elif (
            responses[0] == True and
            responses[1] == False and
            (responses[2] == True or responses[3] == True or responses[7] == True) and
            responses[4] == False and
            responses[5] == False and
            responses[6] == False and
            responses[8] == False

        ):
            return "B"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                (responses[5] == True or (responses[7] == True and responses[8] == True)) and
                responses[6] == False
            ):
                return "C"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == True and
                responses[6] == True and
                responses[7] == False and
                responses[8] == False
            ):
                return "D"
        
        elif (
                responses[0] == True and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == True and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "G"
        
        elif (
                responses[0] == False and
                responses[1] == False and
                responses[2] == False and
                responses[3] == False and
                responses[4] == False and
                responses[5] == False and
                responses[6] == False and
                responses[7] == False and
                responses[8] == False
            ):
                return "Aftermarket"
        
        return "Fully Broken"


    def save(self, *args, **kwargs):
        if not self.grade:
            # Ajoutez ici votre logique pour déterminer la valeur de self.some_condition
            self.some_condition = True  # Remplacez ceci par votre logique réelle

            if self.some_condition:
                # Votre code existant pour déterminer le grade en fonction du type d'écran
                if not self.screenmodel.is_oled and self.screenbrand.screenbrand == 'apple' and not self.screenmodel.is_3dtouch:
                    grade = self.attribuer_grade_not_oled_apple()
                elif not self.screenmodel.is_oled and self.screenbrand.screenbrand == 'apple' and self.screenmodel.is_3dtouch:
                    grade = self.attribuer_grade_not_oled_apple_3dt()
                elif self.screenmodel.is_oled and self.screenbrand.screenbrand == 'apple' and self.screenmodel.is_3dtouch:
                    grade = self.attribuer_grade_oled_apple_3dt()
                elif self.screenmodel.is_oled and self.screenbrand.screenbrand == 'apple' and not self.screenmodel.is_3dtouch:
                    grade = self.attribuer_grade_oled_apple()
                elif not self.screenmodel.is_oled and self.screenbrand.screenbrand != 'apple':
                    grade = self.attribuer_grade_general_not_oled()
                elif self.screenbrand.screenbrand != 'apple' and self.screenmodel.is_oled:
                    grade = self.attribuer_grade_general_oled()
                else:
                    raise Http404()

                print(f"Grade attribué : {grade}")
            self.grade = grade

        print(f"Avant la sauvegarde - Grade : {self.grade}")
        super().save(*args, **kwargs)


    def get_diag_questions_and_responses(self):
        # Ajoutez votre logique pour récupérer les questions et réponses du diagnostic
        questions_and_responses = [
            (1, getattr(self, 'diag_question_1', ''), getattr(self, 'diag_response_1', '')),
            (2, getattr(self, 'diag_question_2', ''), getattr(self, 'diag_response_2', '')),
            (3, getattr(self, 'diag_question_3', ''), getattr(self, 'diag_response_3', '')),
            (4, getattr(self, 'diag_question_4', ''), getattr(self, 'diag_response_4', '')),
            (5, getattr(self, 'diag_question_5', ''), getattr(self, 'diag_response_5', '')),
            (6, getattr(self, 'diag_question_6', ''), getattr(self, 'diag_response_6', '')),
            (7, getattr(self, 'diag_question_7', ''), getattr(self, 'diag_response_7', '')),
            (8, getattr(self, 'diag_question_8', ''), getattr(self, 'diag_response_8', '')),
            (9, getattr(self, 'diag_question_9', ''), getattr(self, 'diag_response_9', '')),
            (10, getattr(self, 'diag_question_10', ''), getattr(self, 'diag_response_10', '')),

            # Ajoutez les autres questions de la même manière
        ]

        return questions_and_responses

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.screenbrand} {self.screenmodel} - {self.grade}"


class Package(models.Model):
    reference = models.CharField(max_length=40, unique=True)
    brokenscreens = models.ManyToManyField('BrokenScreen', related_name='packages')
    date_shipped = models.DateTimeField(auto_now_add=True)
    is_shipped = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Colis - {self.reference}"

    def get_brokenscreen_fields(self):
        brokenscreen_instances = list(self.brokenscreens.all())
        logger.info(f"get_brokenscreen_fields() returned: {type(brokenscreen_instances)}")
        return brokenscreen_instances

    def save(self, *args, **kwargs):
        # Enregistrer le Package pour obtenir un ID avant de calculer total_value
        super().save(*args, **kwargs)
        # Calculer total_value après l'enregistrement
        self.total_value = self.brokenscreens.aggregate(total=Sum('price'))['total'] or 0
        # Appeler save une seule fois après le calcul de total_value
        super().save(*args, **kwargs)

    def paid_package(self):
        # Méthode pour marquer le package comme archivé
        self.is_paid = True

        self.save()


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

class AbonneNewsletter(models.Model):
    email = models.EmailField(unique=True)