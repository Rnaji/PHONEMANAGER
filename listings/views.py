from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods

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
from .forms import RepairStoreForm
from django.contrib.auth.models import User
from .models import UniqueReference
from .signals import UniqueReference, create_new_unique_reference


@login_required
def complete_store_configuration(request):
    registered_username = request.session.get('registered_username', None)

    if request.method == 'POST':
        form = RepairStoreForm(request.POST)
        if form.is_valid():
            store_configuration = form.save(commit=False)

            if registered_username:
                store_configuration.user = User.objects.get(username=registered_username)
                store_configuration.save()

                # Maintenant que le RepairStore est sauvegardé, générez les références uniques
                for _ in range(65):  # Générez 65 références uniques par défaut
                    create_new_unique_reference(store_configuration)

                return redirect('dashboard')

    else:
        form = RepairStoreForm()

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


def page_attente(request):
    # Vue pour le tableau de bord après la connexion
    return render(request, 'page_attente.html')




from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from .models import ScreenBrand, UniqueReference, BrokenScreen, ScreenModel

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
        screenbrand_id = request.POST.get('screenbrand')
        screenmodel_id = request.POST.get('screenmodel')
        uniquereference_id = request.POST.get('uniquereference')

        if screenbrand_id and screenmodel_id and uniquereference_id:
            screenbrand = ScreenBrand.objects.get(pk=screenbrand_id)
            screenmodel = ScreenModel.objects.get(pk=screenmodel_id)
            uniquereference = UniqueReference.objects.get(pk=uniquereference_id)

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

        # Si les données du formulaire ne sont pas valides, vous pouvez ajouter un code ici pour gérer cela.
        # Par exemple, renvoyer un message d'erreur à l'utilisateur.

        context = {
            'brand_list': ScreenBrand.objects.all(),
            'ref_unique_list': UniqueReference.objects.filter(repairstore=request.user.repairstore, is_attributed=False)
        }
        return render(request, self.template_name, context)


from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from .models import ScreenBrand, ScreenModel  # Assurez-vous d'importer vos modèles

import json
import logging
from django.http import HttpResponse, Http404
from django.shortcuts import render

logger = logging.getLogger(__name__)

def htmx_get_modeles_from_brand(request):
    if request.GET.get('brand_field'):
        with open('/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/screen_modele_data.json') as json_file:
            data = json.load(json_file)

        brand_ref = request.GET.get('brand_field')
        logger.debug(f"Brand reference: {brand_ref}")

        modeles_list = data.get(brand_ref, [])
        logger.debug(f"Modeles list: {modeles_list}")

        if modeles_list:
            modele_list_from_brand = '<option selected disabled>Choisir</option>'
            
            for model in modeles_list:
                modele_list_from_brand += f'<option value="{model}">{model}</option>'

            logger.debug(f"Model list from brand: {modele_list_from_brand}")

            return HttpResponse(modele_list_from_brand)
        else:
            logger.warning("La marque n'a pas été trouvée dans le fichier JSON.")
            raise Http404("La marque n'a pas été trouvée dans le fichier JSON.")

    logger.debug("Aucune référence de marque n'a été fournie.")
    return HttpResponse()


