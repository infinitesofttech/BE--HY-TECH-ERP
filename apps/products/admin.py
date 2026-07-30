from django.contrib import admin
from .models import ProductCategory, Product, TourPlan, Policy


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'for_vehicle_type',
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
