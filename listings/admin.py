from django.contrib import admin
from .models import RepairStore, UniqueReference, ScreenBrand, ScreenModel, Recycler, RecyclerPricing, BrokenScreen

@admin.register(RepairStore)
class RepairStoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'address', 'phone_number', 'date_joined']
    search_fields = ['company_name', 'user__username']

@admin.register(UniqueReference)
class UniqueReferenceAdmin(admin.ModelAdmin):
    list_display = ['repairstore', 'value', 'is_used']
    search_fields = ['repairstore__company_name', 'value']

@admin.register(ScreenBrand)
class ScreenBrandAdmin(admin.ModelAdmin):
    list_display = ['screenbrand']
    search_fields = ['screenbrand']

@admin.register(ScreenModel)
class ScreenModelAdmin(admin.ModelAdmin):
    list_display = ['screenbrand', 'screenmodel', 'is_oled', 'is_wanted']
    search_fields = ['screenbrand__screenbrand', 'screenmodel']

@admin.register(Recycler)
class RecyclerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'address', 'phone_number', 'date_joined', 'is_us']
    search_fields = ['company_name']

@admin.register(RecyclerPricing)
class RecyclerPricingAdmin(admin.ModelAdmin):
    list_display = ['recycler', 'screenbrand', 'screenmodel', 'grade', 'price']
    search_fields = ['recycler__company_name', 'screenbrand__screenbrand', 'screenmodel__screenmodel']

@admin.register(BrokenScreen)
class BrokenScreenAdmin(admin.ModelAdmin):
    list_display = ['repairstore', 'uniquereference', 'screenbrand', 'screenmodel', 'is_attributed', 'date_joined']
    search_fields = ['repairstore__company_name', 'screenbrand__screenbrand', 'screenmodel__screenmodel']
