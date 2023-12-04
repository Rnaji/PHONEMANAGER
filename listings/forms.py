# dans votre_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import StoreConfiguration
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    # Ajout du champ email avec une aide contextuelle
    email = forms.EmailField(required=True, help_text='Requis. Entrez une adresse e-mail valide.')

    class Meta:
        model = User
        # Champs à inclure dans le formulaire et leur ordre
        fields = ['username', 'email', 'password1', 'password2']

class StoreConfigurationForm(forms.ModelForm):
    class Meta:
        model = StoreConfiguration
        # Inclure tous les champs du modèle, sauf 'user'
        fields = '__all__' 
        exclude = ['user']
