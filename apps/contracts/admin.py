from django.contrib import admin
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'value', 'status', 'start_date', 'end_date', 'created_by')
    list_filter = ('status',)
    search_fields = ('title', 'client_name')
    list_per_page = 25
