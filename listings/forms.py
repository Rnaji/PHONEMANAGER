# dans votre_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import RepairStore, AbonneNewsletter
from django.contrib.auth.models import User
import logging
from django import forms

class UserRegistrationForm(UserCreationForm):
    # Ajout du champ email avec une aide contextuelle
    email = forms.EmailField(required=True, help_text='Requis. Entrez une adresse e-mail valide.')

    class Meta:
        model = User
        # Champs à inclure dans le formulaire et leur ordre
        fields = ['username', 'email', 'password1']

class RepairStoreForm(forms.ModelForm):
    class Meta:
        model = RepairStore
        # Inclure tous les champs du modèle, sauf 'user'
        fields = '__all__' 
        exclude = ['user']


class CreateBrokenScreenForm(forms.Form):
    brand_field = forms.CharField(label='📱 Marque')
    model_field = forms.CharField(label='📱 Modèle')
    unique_ref_field = forms.IntegerField(label='🏷 Référence unique')

    def __init__(self, *args, **kwargs):
        super(CreateBrokenScreenForm, self).__init__(*args, **kwargs)

        # Ajoutez des attributs pour le style Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mb-3'

        # Ajoutez un attribut supplémentaire pour le champ unique_ref_field
        self.fields['unique_ref_field'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()

        # Pas besoin de convertir en entiers

        # Ajoutez des instructions print pour afficher les données nettoyées
        print("Cleaned Data:", cleaned_data)

        return cleaned_data


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = AbonneNewsletter
        fields = ['email']