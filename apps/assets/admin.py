from django.contrib import admin

from .models import (
    AssetRegistration,
    AssetAssignment,
    AssetDepreciation,
    AssetMaintenance,
    AssetDisposal,
)


@admin.register(AssetRegistration)
class AssetRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'asset_name', 'asset_user', 'category', 'location',
        'purchase_date', 'warranty_end_date', 'warranty', 'status',
    ]
    list_filter = ['status', 'category']
    search_fields = ['asset_name', 'asset_user__email', 'category', 'location']


@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'assignment_id', 'asset', 'assigned_to', 'department',
        'assignment_date', 'return_date', 'status',
    ]
    list_filter = ['status', 'department']
    search_fields = ['assignment_id', 'asset__asset_name', 'assigned_to__email']


@admin.register(AssetDepreciation)
class AssetDepreciationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'depreciation_id', 'asset', 'purchase_cost',
        'accumulated_depreciation', 'net_book_value',
        'depreciation_method', 'useful_life_years', 'status',
    ]
    list_filter = ['depreciation_method', 'status']
    search_fields = ['depreciation_id', 'asset__asset_name']


@admin.register(AssetMaintenance)
class AssetMaintenanceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'maintenance_id', 'asset', 'maintenance_type',
        'scheduled_date', 'status',
    ]
    list_filter = ['maintenance_type', 'status']
    search_fields = ['maintenance_id', 'asset__asset_name', 'remark']


@admin.register(AssetDisposal)
class AssetDisposalAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'disposal_id', 'asset', 'method', 'value', 'date',
        'approved_by', 'status',
    ]
    list_filter = ['method', 'status']
    search_fields = ['disposal_id', 'asset__asset_name']
