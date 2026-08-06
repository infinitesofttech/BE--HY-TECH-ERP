from django.contrib import admin
from .models import (
    Customer, SalesOrder, SalesOrderItem,
    Refund, DeliveryNote, DeliveryNoteItem, CustomerFeedback,
)


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1
    readonly_fields = ['amount', 'tax_amount']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'country', 'created_at']
    list_filter = ['country']
    search_fields = ['name', 'email', 'phone', 'country']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'employee', 'customer', 'date', 'payment_method', 'status',
        'total_amount', 'created_at',
    ]
    list_filter = ['status', 'payment_method', 'date']
    search_fields = ['order_id', 'customer__name', 'employee__email', 'notes']
    readonly_fields = ['order_id', 'total_amount', 'created_at', 'updated_at']
    inlines = [SalesOrderItemInline]


@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'product', 'quantity', 'unit_price',
        'discount', 'amount', 'tax', 'tax_amount',
    ]
    list_filter = ['product']
    readonly_fields = ['amount', 'tax_amount']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = [
        'refund_id', 'customer', 'amount', 'payment_method',
        'status', 'created_at',
    ]
    list_filter = ['status', 'payment_method']
    search_fields = ['refund_id', 'reference', 'customer__name', 'refund_reason']
    readonly_fields = ['refund_id', 'created_at', 'updated_at']


class DeliveryNoteItemInline(admin.TabularInline):
    model = DeliveryNoteItem
    extra = 1
    readonly_fields = ['amount']


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = [
        'delivery_note_id', 'customer', 'invoice_date', 'due_date',
        'frequency', 'status', 'total_amount', 'created_at',
    ]
    list_filter = ['status', 'frequency', 'invoice_date']
    search_fields = ['delivery_note_id', 'reference', 'customer__name']
    readonly_fields = [
        'delivery_note_id', 'total_amount', 'created_at', 'updated_at',
    ]
    inlines = [DeliveryNoteItemInline]


@admin.register(DeliveryNoteItem)
class DeliveryNoteItemAdmin(admin.ModelAdmin):
    list_display = [
        'delivery_note', 'product', 'quantity', 'unit_price',
        'discount', 'amount', 'note',
    ]
    list_filter = ['product']
    readonly_fields = ['amount']


@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('customer', 'subject', 'date', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('subject', 'feedback', 'customer__name')
    readonly_fields = ('created_at', 'updated_at')
