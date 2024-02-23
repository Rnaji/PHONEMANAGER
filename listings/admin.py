from django.contrib import admin
from .models import RepairStore, UniqueReference, ScreenBrand, ScreenModel, Recycler, RecyclerPricing, BrokenScreen, Package, AbonneNewsletter

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
    list_display = ['screenbrand', 'screenmodel', 'is_oled', 'is_wanted', 'is_3dtouch']
    search_fields = ['screenbrand__screenbrand', 'screenmodel']
    list_editable = ['is_oled', 'is_wanted', 'is_3dtouch']
    list_filter = ['screenbrand','is_wanted'] 

@admin.register(Recycler)
class RecyclerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'address', 'phone_number', 'date_joined', 'is_us']
    search_fields = ['company_name']

@admin.register(RecyclerPricing)
class RecyclerPricingAdmin(admin.ModelAdmin):
    list_display = ['recycler_company_name', 'screenbrand', 'screenmodel', 'grade', 'price']
    search_fields = ['recycler__company_name', 'screenbrand__screenbrand', 'screenmodel__screenmodel']
    list_filter = ['recycler__company_name']

    def recycler_company_name(self, obj):
        return obj.recycler.company_name
    recycler_company_name.short_description = 'Recycler Company Name'

@admin.register(BrokenScreen)
class BrokenScreenAdmin(admin.ModelAdmin):
    list_display = ['repairstore', 'uniquereference', 'screenbrand', 'screenmodel','grade', 'is_attributed', 'date_joined','is_packed']
    search_fields = ['repairstore__company_name', 'screenbrand__screenbrand', 'screenmodel__screenmodel']
    list_editable = ['is_packed']
    list_filter = ['repairstore','screenbrand','grade','screenmodel', 'is_attributed'] 


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['reference', 'date_shipped', 'is_shipped', 'is_paid']
    list_filter = ['is_shipped', 'is_paid']
    search_fields = ['reference']

@admin.register(AbonneNewsletter)
class AbonneNewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', )
    search_fields = ('email', )