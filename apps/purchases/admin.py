from django.contrib import admin
from .models import (
    Vendor,
    Purchase, PurchaseItem,
    PurchaseOrder, PurchaseOrderItem,
    PurchaseReturn, PurchaseReturnItem,
)


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'country', 'status')
    list_filter = ('status', 'country')
    search_fields = ('name', 'contact_person', 'email', 'phone', 'country')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'purchase_id', 'vendor', 'requestor', 'date', 'status',
        'total_amount',
    )
    list_filter = ('status', 'payment_terms', 'date')
    search_fields = ('purchase_id', 'reference', 'vendor__name', 'notes')
    inlines = [PurchaseItemInline]


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        'purchase_order_id', 'vendor', 'order_date', 'expected_delivery_date',
        'actual_delivery_date', 'status', 'total_amount',
    )
    list_filter = ('status', 'payment_terms', 'order_date')
    search_fields = ('purchase_order_id', 'reference', 'vendor__name', 'notes')
    inlines = [PurchaseOrderItemInline]


class PurchaseReturnItemInline(admin.TabularInline):
    model = PurchaseReturnItem
    extra = 0


@admin.register(PurchaseReturn)
class PurchaseReturnAdmin(admin.ModelAdmin):
    list_display = (
        'return_id', 'purchase', 'vendor', 'return_date', 'status',
        'total_amount',
    )
    list_filter = ('status', 'return_date')
    search_fields = ('return_id', 'reference', 'vendor__name', 'return_reason')
    inlines = [PurchaseReturnItemInline]
