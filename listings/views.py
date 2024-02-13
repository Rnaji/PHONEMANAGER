#######################
# Importations Django #
#######################

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods, require_GET
from django.views.generic import ListView

################################
# Importations liées au projet #
################################

from .forms import UserRegistrationForm, RepairStoreForm, CreateBrokenScreenForm, NewsletterForm
from .models import (
    ScreenBrand, UniqueReference, BrokenScreen, ScreenModel,
    RecyclerPricing, Recycler, RepairStore, Package
)
from .signals import create_new_unique_reference

#######################
# Autres importations #
#######################

import json
from django.contrib import messages
from django.utils import timezone

##################
# Questions diag #
##################

questions_oled= [
    (0, "xxx", "oui", "non"),
    (1, "L’écran est-il original?", 2, 2),
    (2, "Le tactile est défectueux", 3, 3),
    (3, "L’écran présente des dommages fonctionnels", 4, 4),
    (4, "L’écran a des points noirs", 5, 6),
    (5, "Ces points noirs sont gros", 6, 6),
    (6, "Le 3D Touch est défectueux", 7, 7),
    (7, "L’écran a des ombres persistantes", 8, "fin du diag"),
    (8, "Ces ombres sont presque invisibles", "fin du diag", 9),
    (9, "Ces ombres sont très visibles", "fin du diag", "fin du diag")
]

questions_not_oled = [
    (0, "xxx", "oui", "non"),
    (1, "L’écran est-il original?", 2, 2),
    (2, "L’écran présente des dommages fonctionnel", 3, 3),
    (3, "L’écran a des problèmes de rétroéclairage", 4, 4),
    (4, "L’écran est jaunâtre", 5, 5),
    (5, "Le tactile est défectueux", 6, 6),
    (6, "Le 3D Touch est défectueux", 7, 7),
    (7, "L’écran a des points lumineux ou une distorsion des couleurs", 8, 8),
    (8, "L’écran a des pixels morts", 9,"fin du diag"),
    (9, "L’écran a des Gros pixels morts", "fin du diag", "fin du diag")
]

########################
# Home and Legal Views #
########################

@require_GET
def landing(request):
        return render(request, 'landing_index.html')

@require_GET
def legal(request):
    return render(request, 'landing_legal.html')

#############################################
# User Registration and Configuration Views #
#############################################

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

def inscription_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vous êtes inscrit à la newsletter avec succès!')
            return redirect('landing')  # Assurez-vous de rediriger vers la bonne vue ou URL

    else:
        form = NewsletterForm()

    return render(request, 'landing_index.html', {'form': form})


######################################
# Dashboard and Authentication Views #
######################################

@login_required
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

                # Exclude opportunities with the recycler named "VotreRecycleur"
                if (
                    recycler_prices.exists()
                    and recycler_prices.first().price > current_value
                    and broken_screen.recycler.company_name != "VotreRecycleur"
                ):
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
            'broken_screens': broken_screens,
        }

        return render(request, 'dashboard.html', context)

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
    
def logout_view(request):
    logout(request)
    return redirect('landing')

#######################
# Broken Screen Views #
#######################

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

                return redirect('diagnostic', ref_unique_list=uniquereference.value)

            context = {
                'brand_list': ScreenBrand.objects.all(),
                'ref_unique_list': UniqueReference.objects.filter(repairstore=request.user.repairstore, is_used=False),
                'form': form,
            }
            return render(request, self.template_name, context)

        except Exception as e:
            return JsonResponse({'error': 'Une erreur s\'est produite'}, status=500)
        
@require_GET
def htmx_get_modeles_from_brand(request):
    try:
        if not request.GET.get('brand_field'):
            raise ValueError("Aucune référence de marque n'a été fournie.")

        # Chargez les données depuis le fichier JSON ou votre source de données
        with open('/Users/rachidnaji/PythonProject/projets/PhoneManager/scrap_app/screen_modele_data.json') as json_file:
            data = json.load(json_file)

        brand_ref = request.GET.get('brand_field')

        modeles_list = data.get(brand_ref, [])

        if not modeles_list:
            raise ValueError("La marque n'a pas été trouvée dans le fichier JSON.")

        modele_list_from_brand = '<option selected disabled>Choisir</option>'
        for model in modeles_list:
            modele_list_from_brand += f'<option value="{model}">{model}</option>'

        return HttpResponse(modele_list_from_brand)

    except Exception as e:
        return JsonResponse({'error': 'Une erreur s\'est produite'}, status=500)
    
@login_required
def get_unused_ref_unique_list_view(request):
    current_repairstore = request.user.repairstore
    ref_unique_list = current_repairstore.get_unused_ref_unique_list()

    context = {
        'ref_unique_list': ref_unique_list,
        # Autres éléments du contexte si nécessaire
    }

    return render(request, 'votre_template.html', context)

##################################
# Diagnostic and Quotation Views #
##################################

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
@require_GET
def delete_diagnostic(request, ref_unique_list):
    # Assurez-vous d'obtenir l'instance BrokenScreen correcte
    broken_screen = BrokenScreen.objects.get(uniquereference__value=ref_unique_list)

    # Réinitialiser les valeurs du diagnostic
    for i in range(1, 11):
        setattr(broken_screen, f'diag_response_{i}', '')

    broken_screen.grade = ''
    broken_screen.quotation = None
    broken_screen.is_diag_done = False
    broken_screen.save()

    message_text = 'Le diagnostic a été supprimé'
    messages.add_message(request, messages.SUCCESS, message_text)

    # Rediriger vers la page de diagnostic pour commencer un nouveau diagnostic
    return redirect('diagnostic', ref_unique_list=broken_screen.uniquereference.value)

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

###############
# Stock Views #
###############

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

@login_required
@require_GET
def stock_brand(request, brand_ref):
    # Récupérer la marque spécifique en fonction de la référence
    brand = get_object_or_404(ScreenBrand, screenbrand=brand_ref)

    # Filtrer les instances de BrokenScreen pour l'utilisateur connecté, la marque spécifiée, et non emballées
    broken_screens = BrokenScreen.objects.filter(
        repairstore=request.user.repairstore,
        screenbrand=brand,
        is_packed=False
    ).order_by('screenmodel__screenmodel')

    context = {
        'brand': brand,
        'broken_screens': broken_screens,
        'items_count': broken_screens.count(),
        'items_value': sum(broken_screen.price for broken_screen in broken_screens if broken_screen.price),
    }

    return render(request, 'stock.html', context)

@login_required
@require_GET
def stock_recycler(request, recycler_ref):
    # Récupérer le recycleur spécifique en fonction de la référence
    recycler = get_object_or_404(Recycler, company_name=recycler_ref)

    # Filtrer les instances de BrokenScreen pour l'utilisateur connecté, le recycleur spécifié, et non emballées
    broken_screens = BrokenScreen.objects.filter(
        repairstore=request.user.repairstore,
        recycler=recycler,
        is_packed=False
    ).order_by('screenmodel__screenmodel')

    context = {
        'recycler': recycler,
        'broken_screens': broken_screens,
        'items_count': broken_screens.count(),
        'items_value': sum(broken_screen.price for broken_screen in broken_screens if broken_screen.price),
    }

    return render(request, 'stock.html', context)

#######################
# Opportunities Views #
#######################

@login_required
@require_GET
def opportunities(request):
    # Filtrer les instances de BrokenScreen pour l'utilisateur connecté
    all_broken_screens = BrokenScreen.objects.filter(is_packed=False, repairstore=request.user.repairstore)

    # Exclure les instances avec le recycleur "VotreRecycleur"
    all_broken_screens = all_broken_screens.exclude(recycler__company_name="VotreRecycleur")

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
        # Ajouter des informations sur l'opportunité à chaque instance de BrokenScreen
        broken_screen.quotation_count = broken_screen_op_list[i][3]
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

#########################################
# Broken Screen Detail and Delete Views #
#########################################

@method_decorator(login_required, name='dispatch')
class BrokenScreenDetail(View):
    template_name = 'broken_screen_detail.html'

    def get(self, request, *args, **kwargs):
        # Récupérer l'instance de BrokenScreen avec is_packed=False
        broken_screen = get_object_or_404(BrokenScreen, uniquereference__value=kwargs['uniquereference_value'], is_packed=False)

        # Récupérez les objets RecyclerPricing associés à ce BrokenScreen
        quotations = broken_screen.quotations.filter(grade=broken_screen.grade).all()

        context = {
            'broken_screen': broken_screen,
            'quotations': quotations,
            'recycler': broken_screen.recycler,  # Ajoutez le recycler au contexte
            'diag_questions_and_responses': broken_screen.get_diag_questions_and_responses(),
            'is_oled': broken_screen.screenmodel.is_oled,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Récupérer à nouveau l'instance de BrokenScreen avec is_packed=False
        broken_screen = get_object_or_404(BrokenScreen, uniquereference__value=kwargs['uniquereference_value'], is_packed=False)

        # Ajoutez un message de succès pour informer l'utilisateur que les modifications ont été enregistrées
        messages.success(request, "Les réponses du diagnostic ont été enregistrées avec succès.")

        return redirect('quotation', ref_unique_list=broken_screen.uniquereference.value)

    
@method_decorator(login_required, name='dispatch')
class DeleteBrokenScreen(View):
    template_name = 'delete_brokenscreen.html'

    def get(self, request, uniquereference_value):
        broken_screen = get_object_or_404(BrokenScreen, uniquereference__value=uniquereference_value)
        return render(request, self.template_name, {'broken_screen': broken_screen})

    def post(self, request, uniquereference_value):
        broken_screen = get_object_or_404(BrokenScreen, uniquereference__value=uniquereference_value)
        broken_screen.delete()
        return redirect('dashboard')
    
##################
# Settings Views #
##################
        
@login_required
def settings_view(request):
    repair_store = RepairStore.objects.get(user=request.user)

    # Filtrer les références distinctes des packages associés à la RepairStore
    unique_references = Package.objects.filter(brokenscreens__repairstore=repair_store).values_list('reference', flat=True).distinct()

    # Organiser les informations par référence
    packages_info = {}
    non_paid_packages = []  # Ajouter une liste pour les colis non payés
    paid_packages = []  # Ajouter une liste pour les colis archivés

    total_value_paid = 0  # Initialiser la valeur totale des colis payés

    for reference in unique_references:
        package = Package.objects.filter(
            reference=reference,
            brokenscreens__repairstore=repair_store
        ).first()

        if package:
            brokenscreen_fields = package.get_brokenscreen_fields()
            packages_info[reference] = {
                'package': package,
                'brokenscreen_fields': brokenscreen_fields,
            }

            if not package.is_paid:
                non_paid_packages.append(package)  # Ajouter le colis non payé à la liste
            elif package.is_paid:
                paid_packages.append(package)  # Ajouter le colis archivé à la liste

            if package.is_paid:
                total_value_paid += package.total_value  # Ajouter la valeur totale du colis payé

    has_paid_packages = any(package_info['package'].is_paid for package_info in packages_info.values())

    context = {
        'repair_store': repair_store,
        'packages_info': packages_info,
        'has_paid_packages': has_paid_packages,
        'non_paid_packages': non_paid_packages,  # Ajouter la liste des colis non payés au contexte
        'paid_packages': paid_packages,  # Ajouter la liste des colis archivés au contexte
        'total_value_paid': total_value_paid,  # Ajouter la valeur totale des colis payés au contexte
    }

    return render(request, 'settings_view.html', context)

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

# Stickers Views

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

#################### 
# Expedition Views #
####################
    
@method_decorator(login_required, name='dispatch')
class ExpedierMesEcransView(ListView):
    model = BrokenScreen
    template_name = 'expedier_mes_ecrans.html'
    context_object_name = 'broken_screens'

    def get_queryset(self):
        # Filtrer les instances de BrokenScreen pour l'utilisateur connecté et non emballées
        queryset = BrokenScreen.objects.filter(is_packed=False, repairstore=self.request.user.repairstore)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer les statistiques par recycleur
        recycler_statistics = self.model.objects.filter(repairstore=self.request.user.repairstore, is_packed=False) \
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

@method_decorator(login_required, name='dispatch')
class ExpedierMesEcransRecycler(View):
    template_name = 'expedier_mes_ecrans_recycler.html'

    def get(self, request, *args, **kwargs):
        recycler_ref = kwargs.get('recycler_ref')

        # Récupérer le recycleur spécifique en fonction de la référence
        recycler = get_object_or_404(Recycler, company_name=recycler_ref)

        # Filtrer les instances de BrokenScreen pour l'utilisateur connecté, le recycleur spécifié, et non emballées
        broken_screens = BrokenScreen.objects.filter(
            repairstore=request.user.repairstore,
            recycler=recycler,
            is_packed=False
        ).order_by('screenmodel__screenmodel')

        context = {
            'recycler_ref': recycler_ref,
            'recycler': recycler,
            'broken_screens': broken_screens,
            'items_count': broken_screens.count(),
            'items_value': sum(broken_screen.price for broken_screen in broken_screens if broken_screen.price),
        }

        return render(request, self.template_name, context)
    
@method_decorator(login_required, name='dispatch')
class ValiderExpedition(View):
    template_name = 'valider_expedition.html'

    def get(self, request, *args, **kwargs):
        recycler_ref = kwargs.get('recycler_ref')

        # Récupérer le recycleur spécifique en fonction de la référence
        recycler = get_object_or_404(Recycler, company_name=recycler_ref)

        # Filtrer les instances de BrokenScreen pour l'utilisateur connecté, le recycleur spécifié, et non emballées
        broken_screens = BrokenScreen.objects.filter(
            repairstore=request.user.repairstore,
            recycler=recycler,
            is_packed=False
        ).order_by('screenmodel__screenmodel')

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

        # Filtrer les instances de BrokenScreen pour l'utilisateur connecté, le recycleur spécifié, et non emballées
        broken_screens = BrokenScreen.objects.filter(
            repairstore=request.user.repairstore,
            recycler=recycler,
            is_packed=False
        ).order_by('screenmodel__screenmodel')

        # Utiliser une transaction pour garantir que toutes les opérations se font ensemble ou aucune
        with transaction.atomic():
            # Marquer les écrans cassés comme emballés
            for broken_screen in broken_screens:
                broken_screen.is_packed = True
                broken_screen.save()

            package_reference = f"{recycler_ref}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            package = Package(reference=package_reference, is_shipped=False, is_paid=False)
            package.is_shipped = True  # Mettre à jour is_shipped à True
            package.save()

            # Ajouter les écrans cassés au package
            package.brokenscreens.set(broken_screens)

            # Enregistrer le package pour calculer total_value
            package.save()

        # Rediriger vers une page de confirmation ou une autre vue
        return redirect('settings_view')

#################   
# Package Views #
#################
       
@login_required
def mark_package_as_paid(request, reference):
    # Récupérer le package en fonction de la référence et du repairstore de l'utilisateur connecté
    package = Package.objects.filter(
        reference=reference,
        brokenscreens__repairstore=request.user.repairstore,
    ).first()

    if package:
        # Appeler la méthode d'archivage définie dans le modèle
        package.paid_package()

        messages.success(request, "Le package a été archivé avec succès.")
        return redirect('settings_view')
    else:
        raise Http404("Paid package does not exist")
   
@login_required
@transaction.atomic
def update_package(request, reference):
    package = get_object_or_404(Package, reference=reference)
    brokenscreen_instances = package.get_brokenscreen_fields()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                for brokenscreen_instance in brokenscreen_instances:
                    price_key = f'price_{brokenscreen_instance.uniquereference}'
                    grade_key = f'grade_{brokenscreen_instance.uniquereference}'

                    if price_key in request.POST:
                        new_price = request.POST[price_key]
                        brokenscreen_instance.price = new_price

                    if grade_key in request.POST:
                        new_grade = request.POST[grade_key]
                        brokenscreen_instance.grade = new_grade

                    brokenscreen_instance.save()

                # Mettez à jour la valeur totale du package
                package.total_value = sum([brokenscreen.price for brokenscreen in package.brokenscreens.all()])
                package.save()

                # Si toutes les modifications sont réussies, ajoutez un message flash
                messages.success(request, 'Package mis à jour avec succès.')
                return redirect('settings_view')

        except Exception as e:
            # Gérer les erreurs potentielles lors de la mise à jour des instances
            print(f"An error occurred: {e}")
            messages.error(request, 'Une erreur s\'est produite lors de la mise à jour du package.')

    return render(request, 'update_package.html', {'package': package, 'brokenscreen_instances': brokenscreen_instances})



@login_required
def package_detail(request, reference):
    # Récupérer l'instance de Package avec is_paid=True
    package = get_object_or_404(Package, reference=reference, is_paid=True)

    # Appeler la méthode pour obtenir les écrans cassés associés
    brokenscreens = package.get_brokenscreen_fields()

    # Calculer la valeur totale des écrans cassés dans le package
    total_value_brokenscreens = sum(broken_screen.price for broken_screen in brokenscreens if broken_screen.price)

    context = {
        'package': package,
        'brokenscreens': brokenscreens,
        'num_brokenscreens': len(brokenscreens),
        'total_value_brokenscreens': total_value_brokenscreens,
    }

    return render(request, 'package_detail.html', context)



########################
# Static Content Views #
########################

@require_GET
def about(request):
    return render(request, 'about.html')

@require_GET
def contact(request):
    return render(request, 'contact.html')

@require_GET
def faq(request):
    return render(request, 'faq.html')

@require_GET
def pricing(request):
    return render(request, 'pricing.html')

#############
# Wait Page #
#############

@require_GET
def page_attente(request):
    return render(request, 'page_attente.html')
