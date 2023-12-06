# Importations
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from .models import ScreenBrand, UniqueReference, BrokenScreen, ScreenModel
from .forms import UserRegistrationForm, RepairStoreForm
from .signals import create_new_unique_reference
import json
import logging


# Configuration du système de journalisation
logger = logging.getLogger(__name__)

# Landing views

@require_GET
def landing(request):
    return render(request, 'landing_index.html')

@require_GET
def legal(request):
    return render(request, 'landing_legal.html')

# User Registration views

def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['registered_username'] = user.username
            return redirect('complete_store_configuration')
    else:
        form = UserRegistrationForm()

    return render(request, 'user_registration.html', {'form': form})

# Store Configuration view

@login_required
def complete_store_configuration(request):
    registered_username = request.session.get('registered_username', None)

    if request.method == 'POST':
        form = RepairStoreForm(request.POST)
        if form.is_valid():
            store_configuration = form.save(commit=False)

            if registered_username:
                store_configuration.user = get_object_or_404(User, username=registered_username)
                store_configuration.save()

                # Maintenant que le RepairStore est sauvegardé, générez les références uniques
                for _ in range(65):  # Générez 65 références uniques par défaut
                    create_new_unique_reference(store_configuration)

                return redirect('dashboard')

    else:
        form = RepairStoreForm()

    return render(request, 'complete_store_configuration.html', {'form': form})

# Login view

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, 'Identifiant ou mot de passe incorrect.')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

# Dashboard view

def dashboard(request):
    return render(request, 'dashboard.html')

def page_attente(request):
    return render(request, 'page_attente.html')

# Create Broken Screen view

@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')

class CreateBrokenScreenView(View):
    template_name = 'create_brokenscreen.html'

    def get(self, request, *args, **kwargs):
        context = {
            'brand_list': ScreenBrand.objects.all(),
            'ref_unique_list': UniqueReference.objects.filter(repairstore=request.user.repairstore, is_used=False)
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            screenbrand_id = request.POST.get('screenbrand')
            screenmodel_id = request.POST.get('screenmodel')
            uniquereference_id = request.POST.get('uniquereference')

            if screenbrand_id and screenmodel_id and uniquereference_id:
                screenbrand = get_object_or_404(ScreenBrand, pk=screenbrand_id)
                screenmodel = get_object_or_404(ScreenModel, pk=screenmodel_id)
                uniquereference = get_object_or_404(UniqueReference, pk=uniquereference_id)

                broken_screen = BrokenScreen.objects.create(
                    repairstore=request.user.repairstore,
                    uniquereference=uniquereference,
                    screenbrand=screenbrand,
                    screenmodel=screenmodel,
                    is_used=False
                )

                # Marquer la référence unique comme utilisée
                uniquereference.mark_as_used()

                return HttpResponseRedirect(reverse('page_attente'))

            context = {
                'brand_list': ScreenBrand.objects.all(),
                'ref_unique_list': UniqueReference.objects.filter(repairstore=request.user.repairstore, is_used=False)
            }
            return render(request, self.template_name, context)

        except Exception as e:
            logger.error(f"Erreur dans la vue CreateBrokenScreenView: {e}")
            return JsonResponse({'error': 'Une erreur s\'est produite'}, status=500)

# Autres vues (non modifiées)

# Vue pour obtenir la liste des références uniques non utilisées
@login_required
def get_unused_ref_unique_list_view(request):
    current_repairstore = request.user.repairstore
    ref_unique_list = current_repairstore.get_unused_ref_unique_list()

    context = {
        'ref_unique_list': ref_unique_list,
        # Autres éléments du contexte si nécessaire
    }

    return render(request, 'votre_template.html', context)

# Vue pour obtenir les modèles à partir de la marque (HTMX)
def htmx_get_modeles_from_brand(request):
    try:
        if not request.GET.get('brand_field'):
            raise ValueError("Aucune référence de marque n'a été fournie.")

        with open('/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/screen_modele_data.json') as json_file:
            data = json.load(json_file)

        brand_ref = request.GET.get('brand_field')
        logger.debug(f"Brand reference: {brand_ref}")

        modeles_list = data.get(brand_ref, [])
        logger.debug(f"Modeles list: {modeles_list}")

        if not modeles_list:
            raise ValueError("La marque n'a pas été trouvée dans le fichier JSON.")

        modele_list_from_brand = '<option selected disabled>Choisir</option>'
        for model in modeles_list:
            modele_list_from_brand += f'<option value="{model}">{model}</option>'

        logger.debug(f"Model list from brand: {modele_list_from_brand}")

        return HttpResponse(modele_list_from_brand)

    except Exception as e:
        logger.error(f"Erreur dans la vue htmx_get_modeles_from_brand: {e}")
        return JsonResponse({'error': 'Une erreur s\'est produite'}, status=500)
