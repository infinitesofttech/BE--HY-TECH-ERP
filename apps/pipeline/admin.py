from django.contrib import admin
from .models import (
    PipelineStage, Pipeline, Lead, Deal, DealActivity, Opportunity, Activity,
)


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'probability_default')
    list_filter = ('probability_default',)
    search_fields = ('name',)
    list_per_page = 25


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company_name', 'email', 'phone', 'status', 'source', 'value', 'owner', 'created_at')
    list_filter = ('status', 'source', 'industry', 'visibility')
    search_fields = ('first_name', 'last_name', 'company_name', 'email', 'phone')
    filter_horizontal = ('visible_to',)
    list_per_page = 25


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('name', 'lead', 'value', 'status', 'progress', 'pipeline_stage', 'priority', 'owner', 'expected_close_date')
    list_filter = ('status', 'progress', 'priority', 'pipeline_stage')
    search_fields = ('name', 'description')
    filter_horizontal = ('assignees', 'projects')
    list_per_page = 25


@admin.register(DealActivity)
class DealActivityAdmin(admin.ModelAdmin):
    list_display = ('deal', 'activity_type', 'created_by', 'created_at')
    list_filter = ('activity_type',)
    search_fields = ('deal__name', 'description')
    list_per_page = 25


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name',)
    filter_horizontal = ('stages',)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('opportunity_id', 'name', 'account', 'expected_value', 'stage', 'status', 'owner', 'expected_close_date')
    list_filter = ('stage', 'status')
    search_fields = ('name', 'account', 'opportunity_id')
    list_per_page = 25


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'activity_type', 'owner', 'due_date', 'created_at')
    list_filter = ('activity_type',)
    search_fields = ('title', 'description')
    filter_horizontal = ('guests', 'deals', 'contacts', 'companies')
    list_per_page = 25
