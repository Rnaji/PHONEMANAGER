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
from django.contrib.auth import authenticate, login, logout
from .models import ScreenBrand, UniqueReference, BrokenScreen, ScreenModel, RecyclerPricing, Recycler, RepairStore
from .forms import UserRegistrationForm, RepairStoreForm, CreateBrokenScreenForm
from .signals import create_new_unique_reference
import json
import logging
import requests
from django.contrib import messages
from django.views.generic import ListView



# Configuration du système de journalisation
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def page_attente(request):
    return render(request, 'page_attente.html')

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


# Create Broken Screen view
@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
class CreateBrokenScreenView(View):
    template_name = 'create_brokenscreen.html'

    def get(self, request, *args, **kwargs):
        form = CreateBrokenScreenForm()

        context = {
            'brand_list': ScreenBrand.objects.all(),
            'ref_unique_list': UniqueReference.objects.filter(repairstore=request.user.repairstore, is_used=False),
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            form = CreateBrokenScreenForm(request.POST)

            if form.is_valid():
                cleaned_data = form.cleaned_data

                # Obtenez les instances de modèles à partir des chaînes
                screenbrand = ScreenBrand.objects.get(screenbrand=cleaned_data['brand_field'])
                screenmodel = ScreenModel.objects.get(screenmodel=cleaned_data['model_field'])
                uniquereference = UniqueReference.objects.get(pk=cleaned_data['unique_ref_field'])

                broken_screen = BrokenScreen.objects.create(
                    repairstore=request.user.repairstore,
                    uniquereference=uniquereference,
                    screenbrand=screenbrand,
                    screenmodel=screenmodel,
                    # is_used n'est pas un argument lors de la création
                )

                # Mettez à jour le champ is_used de la référence unique après la création de l'instance
                uniquereference.is_used = True  # ou False, en fonction de la logique de votre application
                uniquereference.save()

                # Ajoutez des instructions print pour afficher les détails de l'écran cassé
                print("Broken Screen Details:", broken_screen.__dict__)
                logging.info("Broken Screen Details: %s", broken_screen.__dict__)

                return redirect('diagnostic', ref_unique_list=uniquereference.value)

            context = {
                'brand_list': ScreenBrand.objects.all(),
                'ref_unique_list': UniqueReference.objects.filter(repairstore=request.user.repairstore, is_used=False),
                'form': form,
            }
            return render(request, self.template_name, context)

        except Exception as e:
            print(f"Erreur dans la vue CreateBrokenScreenView: {e}")
            logging.error("Erreur dans la vue CreateBrokenScreenView: %s", e)
            return JsonResponse({'error': 'Une erreur s\'est produite'}, status=500)



questions_oled= [
    (0, "xxx", "oui", "non"),
    (1, "L’écran est original", 2, 2),
    (2, "Le tactile est défectueux", 3, 3),
    (3, "L’écran présente des dommages fonctionnels", 4, 4),
    (4, "L’écran a des points noirs", 5, 6),
    (5, "Ces points noirs sont gros", 6, 6),
    (6, "L’écran a des ombres persistantes", 7, "fin du diag"),
    (7, "Ces ombres sont presque invisibles", "fin du diag", 8),
    (8, "Ces ombres sont très visibles", "fin du diag", "fin du diag")
]

questions_not_oled = [
    (0, "xxx", "oui", "non"),
    (1, "L’écran est original", 2, 2),
    (2, "L’écran présente des dommages fonctionnel", 3, 3),
    (3, "L’écran a des problèmes de rétroéclairage", 4, 4),
    (4, "L’écran est jaunâtre", 5, 5),
    (5, "Le tactile est défectueux", 6, 6),
    (6, "Le 3D Touch est défectueux", 7, 7),
    (7, "L’écran a des points lumineux ou une distorsion des couleurs", 8, 8),
    (8, "L’écran a des pixels morts", 9,"fin du diag"),
    (9, "L’écran a des Gros pixels morts", "fin du diag", "fin du diag")
]

@login_required
@require_http_methods(['GET', 'POST'])
def diagnostic(request, ref_unique_list):
    # Assurez-vous d'obtenir l'instance BrokenScreen correcte
    broken_screen = BrokenScreen.objects.get(uniquereference__value=ref_unique_list)

    # Si le diagnostic est déjà effectué, renvoyez à la page quotation
    if broken_screen.is_diag_done:
        message_text = 'Le diagnostic a déjà été effectué'
        messages.add_message(request, messages.ERROR, message_text)
        return redirect('quotation', ref_unique_list=broken_screen.uniquereference.value)

    # Définir le jeu de question oled ou non oled
    if broken_screen.screenmodel.is_oled:
        questions_set = questions_oled
    elif not broken_screen.screenmodel.is_oled:
        questions_set = questions_not_oled
    else:
        raise Http404()

    # Début méthode GET
    if request.method == "GET":
        qid = 1
        template = 'diagnostic.html'
        context = {
            'qid': qid,
            'broken_screen': broken_screen,
            'question_number': questions_set[qid][0],
            'question': questions_set[qid][1],
        }
        return render(request, template, context)

    # Début méthode POST
    elif request.method == "POST":
        qid = int(request.POST['qid'])
        la_reponse = request.POST['la_reponse']
        if la_reponse == 'oui':
            diag_response = True
            la_suite = questions_set[qid][2]
        elif la_reponse == 'non':
            diag_response = False
            la_suite = questions_set[qid][3]
        else:
            raise Http404()

        # Enregistrer question et réponse
        if qid not in range(1, 11):
            raise Http404()
        else:
            setattr(broken_screen, f'diag_question_{qid}', questions_set[qid][1])
            setattr(broken_screen, f'diag_response_{qid}', diag_response)

        broken_screen.save()

        # Redirection vers la question suivante
        if isinstance(la_suite, int):
            print("La suite est de type int.")
            template = 'diagnostic.html'
            context = {
                'qid': la_suite,
                'item': broken_screen,
                'question_number': questions_set[la_suite][0],
                'question': questions_set[la_suite][1],
            }
            return render(request, template, context)

        elif isinstance(la_suite, str):
            if la_suite in ["fin du diag"]:
                # Déterminez le jeu de questions en fonction du type d'écran
                if broken_screen.screenmodel.is_oled:
                    grade = broken_screen.attribuer_grade_oled()
                else:
                    grade = broken_screen.attribuer_grade_non_oled()

                print(f"Grade attribué : {grade}")
                broken_screen.grade = grade

                broken_screen.is_diag_done = True
                broken_screen.save()
                messages.add_message(request, messages.SUCCESS, "Diagnostic terminé avec succès !")
                return redirect('quotation', ref_unique_list=broken_screen.uniquereference.value)

    else:
        raise Http404()

        
@login_required
def quotation(request, ref_unique_list):
    broken_screen = get_object_or_404(BrokenScreen, uniquereference__value=ref_unique_list)

    # Obtenez les prix des recycleurs liés au modèle et à la marque de l'écran cassé
    recycler_prices = RecyclerPricing.objects.filter(
        screenbrand=broken_screen.screenbrand,
        screenmodel=broken_screen.screenmodel,
        grade=broken_screen.grade
    )

    # Ajoutez les offres de rachat à la relation quotations de BrokenScreen
    broken_screen.quotations.add(*recycler_prices)

    context = {
        'recycler_prices': recycler_prices,
        'broken_screen': broken_screen,
    }
    return render(request, 'quotation.html', context)



def screen_offre(request, ref_unique_list, recycler_price_id):
    broken_screen = get_object_or_404(BrokenScreen, uniquereference__value=ref_unique_list)
    recycler_price = get_object_or_404(RecyclerPricing, id=recycler_price_id)

    context = {
        'broken_screen': broken_screen,
        'recycler_price': recycler_price,
    }

    # Mettez à jour is_attributed et enregistrez le prix et le recycler lorsqu'un utilisateur choisit une offre de rachat
    if not broken_screen.is_attributed or (
        broken_screen.price != recycler_price.price or
        broken_screen.recycler != recycler_price.recycler
    ):
        broken_screen.is_attributed = True
        broken_screen.price = recycler_price.price  # Enregistrez le nouveau prix choisi
        broken_screen.recycler = recycler_price.recycler  # Enregistrez le nouveau recycler choisi

        broken_screen.save()

    return render(request, 'screen_offre.html', context)



@login_required
def stock_all(request):
    # Récupérer toutes les instances de BrokenScreen créées par l'utilisateur actuel
    broken_screens = BrokenScreen.objects.filter(repairstore__user=request.user, is_packed=False)

    context = {
        'broken_screens': broken_screens,
        'items_count': broken_screens.count(),  # Vous pouvez ajuster cela en fonction de vos besoins
        'items_value': sum(broken_screen.price for broken_screen in broken_screens if broken_screen.price),
    }

    return render(request, 'stock.html', context)



import logging
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

def stock_brand(request, brand_ref):
    # Récupérer la marque spécifique en fonction de la référence
    brand = get_object_or_404(ScreenBrand, screenbrand=brand_ref)
    logger.debug(f"Brand: {brand}")

    # Récupérer toutes les instances de BrokenScreen liées à cette marque, triées par modèle
    broken_screens = BrokenScreen.objects.filter(screenbrand=brand, is_packed=False).order_by('screenmodel__screenmodel')
    logger.debug(f"Broken screens: {broken_screens}")

    context = {
        'brand': brand,
        'broken_screens': broken_screens,
        'items_count': broken_screens.count(),
        'items_value': sum(broken_screen.price for broken_screen in broken_screens if broken_screen.price),
    }

    return render(request, 'stock.html', context)


def stock_recycler(request, recycler_ref):
    # Récupérer le recycleur spécifique en fonction de la référence
    recycler = get_object_or_404(Recycler, company_name=recycler_ref)
    logger.debug(f"Recycler: {recycler}")

    # Récupérer toutes les instances de BrokenScreen liées à ce recycleur, triées par modèle
    broken_screens = BrokenScreen.objects.filter(recycler=recycler, is_packed=False).order_by('screenmodel__screenmodel')
    logger.debug(f"Broken screens: {broken_screens}")

    context = {
        'recycler': recycler,
        'broken_screens': broken_screens,
        'items_count': broken_screens.count(),
        'items_value': sum(broken_screen.price for broken_screen in broken_screens if broken_screen.price),
    }

    return render(request, 'stock.html', context)





# Dashboard view

from django.db.models import Count, Sum
from django.shortcuts import render



def dashboard(request):
    # Récupérer toutes les instances de BrokenScreen pour l'utilisateur actuel
    broken_screens = BrokenScreen.objects.filter(repairstore__user=request.user, is_packed=False)

    # Récupérer les statistiques par marque
    brand_statistics = broken_screens.values('screenmodel__screenbrand').annotate(
        items_count_brand=Count('screenmodel__screenbrand'),
        total_value=Sum('price')
    )

    # Récupérer les statistiques par recycleur
    recycler_statistics = broken_screens.values('recycler__company_name').annotate(
        items_count_recycler=Count('recycler__company_name'),
        items_count_brand=Count('screenmodel__screenbrand'),
        total_value_recycler=Sum('price')
    )

    # Calculer le nombre total d'articles et la valeur totale
    items_count = broken_screens.count()
    items_value = broken_screens.aggregate(total_value=Sum('price'))['total_value'] or 0

    # Opportunités
    opportunities_count = 0
    opportunities_value = 0
    broken_screen_op_list = []

    for broken_screen in broken_screens:
        if broken_screen.price is not None:
            current_value = broken_screen.price
            recycler_prices = RecyclerPricing.objects.filter(
                screenmodel=broken_screen.screenmodel,
                grade=broken_screen.grade
            ).order_by('-price')

            if recycler_prices.exists() and recycler_prices.first().price > current_value:
                quotation_count = recycler_prices.count()
                best_offer = recycler_prices.first()

                broken_screen.quotation_count = quotation_count
                broken_screen.best_offer = best_offer
                broken_screen.offer_delta = best_offer.price - current_value
                opportunities_count += 1
                opportunities_value += broken_screen.offer_delta
                broken_screen_op_list.append([
                    broken_screen.uniquereference.value,
                    broken_screen.best_offer,
                    broken_screen.offer_delta,
                    broken_screen.quotation_count
                ])

    context = {
        'items_count': items_count,
        'items_value': items_value,
        'recap_brand_table': brand_statistics,
        'recap_recycler_table': recycler_statistics,
        'opportunities_count': opportunities_count,
        'opportunities_value': opportunities_value,
    }

    return render(request, 'dashboard.html', context)


class BrokenScreenDetail(View):
    template_name = 'broken_screen_detail.html'

    def get(self, request, *args, **kwargs):
        # Récupérer l'instance de BrokenScreen avec is_packed=False
        broken_screen = get_object_or_404(BrokenScreen, uniquereference__value=kwargs['uniquereference_value'], is_packed=False)
        

        # Récupérez les objets RecyclerPricing associés à ce BrokenScreen
        quotations = broken_screen.quotations.all()

        context = {
            'broken_screen': broken_screen,
            'quotations': quotations,
            'recycler': broken_screen.recycler,  # Ajoutez le recycler au contexte
        }

        return render(request, self.template_name, context)




class DeleteBrokenScreen(View):
    template_name = 'delete_brokenscreen.html'

    def get(self, request, uniquereference_value):
        broken_screen = get_object_or_404(BrokenScreen, uniquereference__value=uniquereference_value)
        return render(request, self.template_name, {'broken_screen': broken_screen})

    def post(self, request, uniquereference_value):
        broken_screen = get_object_or_404(BrokenScreen, uniquereference__value=uniquereference_value)
        broken_screen.delete()
        return redirect('dashboard')


class ExpedierMesEcransView(ListView):
    model = BrokenScreen
    template_name = 'expedier_mes_ecrans.html'
    context_object_name = 'broken_screens'

    def get_queryset(self):
        # Récupérer les instances de BrokenScreen avec is_packed=False
        queryset = BrokenScreen.objects.filter(is_packed=False, repairstore__user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer les statistiques par recycleur
        recycler_statistics = self.model.objects.filter(repairstore__user=self.request.user, is_packed=False) \
            .values('recycler__company_name') \
            .annotate(
                items_count_recycler=Count('recycler__company_name'),
                items_count_brand=Count('screenmodel__screenbrand'),
                total_value_recycler=Sum('price')
            )

        context.update({
            'recap_recycler_table': recycler_statistics,
        })

        return context




class ExpedierMesEcransRecycler(View):
    template_name = 'expedier_mes_ecrans_recycler.html'

    def get(self, request, *args, **kwargs):
        recycler_ref = kwargs.get('recycler_ref')

        # Récupérer le recycleur spécifique en fonction de la référence
        recycler = get_object_or_404(Recycler, company_name=recycler_ref)

        # Récupérer toutes les instances de BrokenScreen liées à ce recycleur avec is_packed=False, triées par modèle
        broken_screens = BrokenScreen.objects.filter(recycler=recycler, is_packed=False).order_by('screenmodel__screenmodel')

        context = {
            'recycler_ref': recycler_ref,
            'recycler': recycler,
            'broken_screens': broken_screens,
            'items_count': broken_screens.count(),
            'items_value': sum(broken_screen.price for broken_screen in broken_screens if broken_screen.price),
        }

        return render(request, self.template_name, context)



class ValiderExpedition(View):
    template_name = 'valider_expedition.html'

    def get(self, request, *args, **kwargs):
        recycler_ref = kwargs.get('recycler_ref')

        # Récupérer le recycleur spécifique en fonction de la référence
        recycler = get_object_or_404(Recycler, company_name=recycler_ref)

        # Récupérer toutes les instances de BrokenScreen liées à ce recycleur avec is_packed=False, triées par modèle
        broken_screens = BrokenScreen.objects.filter(recycler=recycler, is_packed=False).order_by('screenmodel__screenmodel')

        context = {
            'recycler_ref': recycler_ref,
            'recycler': recycler,
            'broken_screens': broken_screens,
            'items_count': broken_screens.count(),
            'items_value': sum(broken_screen.price for broken_screen in broken_screens if broken_screen.price),
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        recycler_ref = kwargs.get('recycler_ref')

        # Récupérer le recycleur spécifique en fonction de la référence
        recycler = get_object_or_404(Recycler, company_name=recycler_ref)

        # Récupérer toutes les instances de BrokenScreen liées à ce recycleur avec is_packed=False, triées par modèle
        broken_screens = BrokenScreen.objects.filter(recycler=recycler, is_packed=False).order_by('screenmodel__screenmodel')

        # Modifier le champ is_packed de ces instances à True
        for broken_screen in broken_screens:
            broken_screen.is_packed = True
            broken_screen.save()

        # Rediriger vers une page de confirmation ou une autre vue
        return redirect('dashboard')



@login_required
@require_GET
def opportunities(request):
    all_broken_screens = BrokenScreen.objects.filter(is_packed=False)

    # Opportunités
    opportunities_count = 0
    opportunities_value = 0
    broken_screen_op_list = []

    for broken_screen in all_broken_screens:
        if broken_screen.price is not None:
            current_value = broken_screen.price
            recycler_prices = RecyclerPricing.objects.filter(
                screenmodel=broken_screen.screenmodel,
                grade=broken_screen.grade
            ).order_by('-price')

            if recycler_prices.exists() and recycler_prices.first().price > current_value:
                quotation_count = recycler_prices.count()
                best_offer = recycler_prices.first()

                broken_screen.quotation_count = quotation_count
                broken_screen.best_offer = best_offer
                broken_screen.offer_delta = best_offer.price - current_value
                opportunities_count += 1
                opportunities_value += broken_screen.offer_delta
                broken_screen_op_list.append([
                    broken_screen.uniquereference.value,
                    broken_screen.best_offer,
                    broken_screen.offer_delta,
                    broken_screen.quotation_count
                ])

    ref_op_list = [broken_screen[0] for broken_screen in broken_screen_op_list]
    op_all_broken_screens = all_broken_screens.filter(uniquereference__value__in=ref_op_list)
    i = 0

    for broken_screen in op_all_broken_screens:
        # add badge_color on broken_screen
        broken_screen.quotation_count = broken_screen_op_list[i][3]
        # opportunities
        broken_screen.best_offer = broken_screen_op_list[i][1]
        broken_screen.offer_delta = broken_screen_op_list[i][2]
        i += 1

    template = 'opportunities.html'
    context = {
        'all_broken_screens': op_all_broken_screens,
        'opportunities_count': opportunities_count,
        'opportunities_value': opportunities_value,
    }
    return render(request, template, context)










@login_required
@require_GET
def delete_diagnostic(request, ref_unique_list):
    # Assurez-vous d'obtenir l'instance BrokenScreen correcte
    broken_screen = BrokenScreen.objects.get(ref_unique_list=ref_unique_list)

    # Réinitialiser les valeurs du diagnostic
    for i in range(1, 11):
        setattr(broken_screen, f'diag_response_{i}', '')

    broken_screen.grade = ''
    broken_screen.quotation = None
    broken_screen.is_diag_done = False
    broken_screen.save()

    message_text = 'Le diagnostic a été supprimé'
    messages.add_message(request, messages.SUCCESS, message_text)
    return redirect('diagnostic', ref_unique_list=broken_screen.uniquereference.value)
	









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

    
@require_GET
def htmx_get_modeles_from_brand(request):
    try:
        logger.info("Vue Django appelée !")

        if not request.GET.get('brand_field'):
            raise ValueError("Aucune référence de marque n'a été fournie.")

        logger.debug("Requête reçue pour récupérer les modèles.")

        # Chargez les données depuis le fichier JSON ou votre source de données
        with open('/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/screen_modele_data.json') as json_file:
            data = json.load(json_file)

        brand_ref = request.GET.get('brand_field')
        logger.info(f"Brand reference: {brand_ref}")

        modeles_list = data.get(brand_ref, [])
        logger.info(f"Modeles list: {modeles_list}")

        if not modeles_list:
            raise ValueError("La marque n'a pas été trouvée dans le fichier JSON.")

        modele_list_from_brand = '<option selected disabled>Choisir</option>'
        for model in modeles_list:
            modele_list_from_brand += f'<option value="{model}">{model}</option>'

        logger.info(f"Model list from brand: {modele_list_from_brand}")

        return HttpResponse(modele_list_from_brand)

    except Exception as e:
        logger.error(f"Erreur dans la vue htmx_get_modeles_from_brand: {e}")
        return JsonResponse({'error': 'Une erreur s\'est produite'}, status=500)
    

@login_required
def settings_view(request):
    repair_store = RepairStore.objects.get(user=request.user)
    return render(request, 'settings_view.html', {'repair_store': repair_store})

@login_required
def settings_edit_view(request):
    repair_store = RepairStore.objects.get(user=request.user)

    if request.method == 'POST':
        form = RepairStoreForm(request.POST, instance=repair_store)
        if form.is_valid():
            form.save()
            return redirect('settings_view')  # Rediriger vers la vue d'affichage après la modification
    else:
        form = RepairStoreForm(instance=repair_store)

    return render(request, 'settings_edit_view.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('landing') 



@login_required
@require_http_methods(['GET'])
def stickers(request):
    try:
        # Récupérer le magasin de réparation associé à l'utilisateur connecté
        repairstore = RepairStore.objects.get(user=request.user)
        
        # Récupérer les références uniques non utilisées spécifiques au magasin de réparation
        stickers = UniqueReference.objects.filter(repairstore=repairstore, is_used=False)
        
        template = 'stickers.html'
        context = {
            'stickers': stickers,
        }

        return render(request, template, context)
    except RepairStore.DoesNotExist:
        # Gérer le cas où l'utilisateur n'a pas de magasin de réparation associé
        return render(request, 'error_page.html', {'error_message': 'User has no associated RepairStore'})
    

