from django.contrib import admin
from .models import (
    Dealer, Retailer, Currency, Source, Industry,
    ContactStage, LostReason, CallReason, CallLog,
)


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


@admin.register(ContactStage)
class ContactStageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title',)


@admin.register(LostReason)
class LostReasonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title',)


@admin.register(CallReason)
class CallReasonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title',)


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'call_type', 'duration', 'date_time', 'created_at')
    list_filter = ('call_type',)
    search_fields = ('name', 'phone', 'notes')
