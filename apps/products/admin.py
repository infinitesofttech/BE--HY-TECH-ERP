from django.contrib import admin
from .models import (
    ProductCategory, Product, TourPlan, Policy, Warehouse, Supplier, Inventory,
    StockAdjustment, StockTransfer,
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'category', 'price', 'for_vehicle_type',
        'status', 'is_active',
    ]
    list_filter = ['category', 'for_vehicle_type', 'status', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TourPlan)
class TourPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'tour_type', 'duration_days', 'is_active', 'created_at']
    list_filter = ['tour_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'created_at', 'updated_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'capacity', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'contact_person', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'country', 'status', 'created_at']
    list_filter = ['status', 'country']
    search_fields = ['name', 'email', 'phone', 'country']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'warehouse', 'product']
    search_fields = ['product__name', 'warehouse__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'reason', 'difference', 'adjustment_date']
    list_filter = ['reason', 'warehouse', 'adjustment_date']
    search_fields = ['product__name', 'warehouse__name']
    readonly_fields = ['created_at']


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'from_warehouse', 'to_warehouse', 'quantity',
        'transfer_date', 'status',
    ]
    list_filter = ['status', 'from_warehouse', 'to_warehouse', 'transfer_date']
    search_fields = ['product__name', 'from_warehouse__name', 'to_warehouse__name']
    readonly_fields = ['created_at', 'updated_at']
