from django.contrib import admin
from django.urls import path
from .views import landing, legal, user_registration, complete_store_configuration, dashboard, page_attente, CreateBrokenScreenView, htmx_get_modeles_from_brand, get_unused_ref_unique_list_view


from django.contrib.auth.views import LoginView

app_name = 'listings'

urlpatterns = [
    # Administration
    path('admin/', admin.site.urls),

    # URLs de la page d'accueil
    path('', landing, name='landing'),
    path('legal/', legal, name='legal'),

    # URLs d'enregistrement et de configuration de l'utilisateur
    path('user_registration/', user_registration, name='user_registration'),
    path('complete_store_configuration/', complete_store_configuration, name='complete_store_configuration'),

    # URL du tableau de bord
    path('dashboard/', dashboard, name='dashboard'),

    # URL de connexion utilisant la vue de connexion intégrée de Django
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),

    # URL de connexion alternative en utilisant une vue personnalisée (login_view)
    # path('login/', login_view, name='login'),

    # URL attente
    path('page_attente/', page_attente, name='page_attente'),

    path('create_brokenscreen/', CreateBrokenScreenView.as_view(), name='create_brokenscreen'),

    path('htmx_get_modeles_from_brand/', htmx_get_modeles_from_brand, name='htmx_get_modeles_from_brand'),

    path('get_unused_ref_unique_list/', get_unused_ref_unique_list_view, name='get_unused_ref_unique_list'),
]
