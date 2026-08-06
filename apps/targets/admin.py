from django.contrib import admin
from .models import Target, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'team_lead', 'target_revenue', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name']
    filter_horizontal = ['members']


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'employee', 'team', 'month', 'year',
        'target_amount', 'achieved_amount', 'status', 'product', 'created_at',
    ]
    list_filter = ['month', 'year', 'status', 'product', 'employee', 'team']
    search_fields = ['employee__email', 'employee__first_name', 'employee__last_name']
    ordering = ['-year', '-month']
