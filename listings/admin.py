from django.contrib import admin
from .models import StoreConfiguration


@admin.register(StoreConfiguration)
class StoreConfigurationAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'address', 'city', 'phone_number', 'date_joined')
