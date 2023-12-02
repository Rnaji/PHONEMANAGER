from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StoreConfiguration


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requis. Entrez une adresse e-mail valide.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# dans votre_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import StoreConfiguration

class StoreConfigurationForm(forms.ModelForm):
    class Meta:
        model = StoreConfiguration
        fields = '__all__' 
