from django.shortcuts import render
from django.views.decorators.http import require_GET

# Landing views

@require_GET
def landing(request):
    # Vue pour la page d'accueil
    return render(request, 'landing_index.html')

@require_GET
def legal(request):
    # Vue pour la page des mentions légales
    return render(request, 'landing_legal.html')


# User Registration views
# Ces vues concernent le processus d'enregistrement d'un utilisateur

from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm
from django.shortcuts import redirect

def user_registration(request):
    # Vue pour l'enregistrement de l'utilisateur
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Enregistrez l'utilisateur
            user = form.save()

            # Connectez l'utilisateur
            login(request, user)

            # Stockez le nom d'utilisateur dans la session
            request.session['registered_username'] = user.username

            # Redirigez vers la configuration complète du magasin
            return redirect('complete_store_configuration')
    else:
        form = UserRegistrationForm()

    return render(request, 'user_registration.html', {'form': form})


# Store Configuration view
# Cette vue permet à l'utilisateur de configurer son magasin après l'enregistrement

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import StoreConfigurationForm
from django.contrib.auth.models import User

@login_required
def complete_store_configuration(request):
    # Récupérez le nom d'utilisateur depuis la session
    registered_username = request.session.get('registered_username', None)

    if request.method == 'POST':
        form = StoreConfigurationForm(request.POST)
        if form.is_valid():
            # Enregistrez la configuration du magasin
            store_configuration = form.save(commit=False)

            # Assurez-vous que l'utilisateur est bien enregistré
            if registered_username:
                # Définissez le champ user en fonction de l'utilisateur connecté
                store_configuration.user = User.objects.get(username=registered_username)
                store_configuration.save()

            # Redirigez vers le tableau de bord
            return redirect('dashboard')
    else:
        form = StoreConfigurationForm()

    return render(request, 'complete_store_configuration.html', {'form': form})


# Login view
# Vue pour la connexion d'un utilisateur déjà enregistré

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            # Authentifiez l'utilisateur
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                # Connectez l'utilisateur
                login(request, user)
                # Redirigez vers le tableau de bord après la connexion
                return redirect('dashboard')
            else:
                form.add_error(None, 'Identifiant ou mot de passe incorrect.')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


# Dashboard view
# Vue pour la page principale après la connexion

from django.shortcuts import render

def dashboard(request):
    # Vue pour le tableau de bord après la connexion
    return render(request, 'dashboard.html')
