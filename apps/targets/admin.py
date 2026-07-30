from django.contrib import admin
from .models import Target


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'employee', 'month', 'year',
        'target_amount', 'achieved_amount', 'status', 'product', 'created_at',
    ]
    list_filter = ['month', 'year', 'status', 'product', 'employee']
    search_fields = ['employee__email', 'employee__first_name', 'employee__last_name']
    ordering = ['-year', '-month']
