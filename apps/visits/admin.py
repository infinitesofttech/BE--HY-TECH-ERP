from django.contrib import admin
from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'visit_type', 'check_in_time', 'status')
    list_filter = ('visit_type', 'status')
    search_fields = ('employee__email', 'purpose')
    list_per_page = 25
