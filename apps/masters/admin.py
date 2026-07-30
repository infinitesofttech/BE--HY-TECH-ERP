from django.contrib import admin
from .models import Dealer, Retailer, Mechanic, TaxRate, Currency, Source, Industry


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'pin_code', 'status', 'assigned_to')
    list_filter = ('status', 'city')
    search_fields = ('name', 'contact_person', 'city', 'pin_code')
    list_per_page = 25


@admin.register(Retailer)
class RetailerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'pin_code', 'status', 'assigned_to')
    list_filter = ('status', 'city')
    search_fields = ('name', 'contact_person', 'city', 'pin_code')
    list_per_page = 25


@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'pin_code', 'status', 'assigned_to')
    list_filter = ('status', 'city')
    search_fields = ('name', 'contact_person', 'city', 'pin_code')
    list_per_page = 25


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rate', 'type', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'symbol', 'exchange_rate', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'is_active')
    list_filter = ('source_type', 'is_active')
    search_fields = ('name',)


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
