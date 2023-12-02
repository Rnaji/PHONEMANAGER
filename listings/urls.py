"""
URL configuration for prophonemanager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from .views import user_registration
from .views import complete_store_configuration



app_name = 'listings'

urlpatterns = [

    path('admin/', admin.site.urls),

        # Landing urls

    path('', views.landing, name='landing'),
    path('legal/', views.legal, name='legal'),


    path('user_registration/', user_registration, name='user_registration'),
    path('complete_store_configuration/', complete_store_configuration, name='complete_store_configuration'),

]
