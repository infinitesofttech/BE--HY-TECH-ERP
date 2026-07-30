from django.contrib import admin
from .models import PipelineStage, Lead, Deal, DealActivity


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'probability_default')
    list_filter = ('order',)
    search_fields = ('name',)
    list_per_page = 25


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'email', 'phone', 'status', 'source', 'value', 'owner', 'created_at')
    list_filter = ('status', 'source', 'industry', 'visibility')
    search_fields = ('name', 'company_name', 'email', 'phone')
    list_per_page = 25


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('name', 'lead', 'value', 'status', 'stage', 'pipeline_stage', 'priority', 'owner', 'expected_close_date')
    list_filter = ('status', 'stage', 'priority', 'pipeline_stage')
    search_fields = ('name', 'description')
    list_per_page = 25


@admin.register(DealActivity)
class DealActivityAdmin(admin.ModelAdmin):
    list_display = ('deal', 'activity_type', 'created_by', 'created_at')
    list_filter = ('activity_type',)
    search_fields = ('deal__name', 'description')
    list_per_page = 25
