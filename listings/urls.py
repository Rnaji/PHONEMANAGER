from django.contrib import admin
from django.urls import path
from .views import (
    landing, legal, user_registration, complete_store_configuration, dashboard, 
    page_attente, CreateBrokenScreenView, htmx_get_modeles_from_brand, 
    get_unused_ref_unique_list_view, diagnostic, delete_diagnostic, 
    quotation, screen_offre, stock_all, stock_brand, stock_recycler, 
    opportunities, BrokenScreenDetail, DeleteBrokenScreen, 
    ExpedierMesEcransView, ExpedierMesEcransRecycler, settings_view, 
    settings_edit_view, logout_view, stickers, ValiderExpedition, 
    mark_package_as_paid, update_package, about, contact, faq, pricing
)
from django.contrib.auth.views import LoginView

app_name = 'listings'

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),

    # Home and Legal URLs
    path('', landing, name='landing'),
    path('legal/', legal, name='legal'),

    # User Registration and Configuration URLs
    path('user_registration/', user_registration, name='user_registration'),
    path('complete_store_configuration/', complete_store_configuration, name='complete_store_configuration'),

    # Dashboard and Authentication URLs
    path('dashboard/', dashboard, name='dashboard'),

    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', logout_view, name='logout_view'),

    # Broken Screen URLs
    path('create_brokenscreen/', CreateBrokenScreenView.as_view(), name='create_brokenscreen'),
    path('htmx_get_modeles_from_brand/', htmx_get_modeles_from_brand, name='htmx_get_modeles_from_brand'),
    path('get_unused_ref_unique_list/', get_unused_ref_unique_list_view, name='get_unused_ref_unique_list'),

    # Diagnostic and Quotation URLs
    path('diagnostic/<ref_unique_list>/', diagnostic, name='diagnostic'),
    path('diagnostic/delete/<ref_unique_list>/', delete_diagnostic, name='delete_diagnostic'),
    path('quotation/<ref_unique_list>/', quotation, name='quotation'),
    path('screen/<ref_unique_list>/offre/<recycler_price_id>/', screen_offre, name='screen_offre'),

    # Stock URLs
    path('stock/all/', stock_all, name='stock_all'),
    path('stock/brand/<brand_ref>/', stock_brand, name='stock_brand'),
    path('stock/recycler/<recycler_ref>/', stock_recycler, name='stock_recycler'),

    # Opportunities URL
    path('opportunities/', opportunities, name='opportunities'),

    # Broken Screen Detail and Delete URLs
    path('brokenscreen/detail/<uniquereference_value>/', BrokenScreenDetail.as_view(), name='broken_screen_detail'),
    path('brokenscreen/delete/<uniquereference_value>/', DeleteBrokenScreen.as_view(), name='delete_brokenscreen'),

    # Settings URLs
    path('settings/', settings_view, name='settings_view'),
    path('settings/edit/', settings_edit_view, name='settings_edit_view'),

    # Stickers URL
    path('stickers/', stickers, name='stickers'),

    # Expedition URLs
    path('expedier_mes_ecrans/', ExpedierMesEcransView.as_view(), name='expedier_mes_ecrans'),
    path('expedier_mes_ecrans/recycler/<recycler_ref>/', ExpedierMesEcransRecycler.as_view(), name='expedier_mes_ecrans_recycler'),
    path('valider_expedition/recycler/<recycler_ref>/', ValiderExpedition.as_view(), name='valider_expedition'),

    # Package URLs
    path('mark_package_as_paid/<str:reference>/', mark_package_as_paid, name='mark_package_as_paid'),
    path('update_package/<str:reference>/', update_package, name='update_package'),

    # Static Content URLs
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('faq/', faq, name='faq'),
    path('pricing/', pricing, name='pricing'),

    # Wait Page URL
    path('page_attente/', page_attente, name='page_attente'),
]

