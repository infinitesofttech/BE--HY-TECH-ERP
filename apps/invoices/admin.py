from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['total']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'customer_name', 'invoice_date', 'due_date',
        'total', 'status', 'created_by', 'created_at',
    ]
    list_filter = ['status', 'invoice_date', 'due_date']
    search_fields = ['invoice_number', 'customer_name', 'customer_email']
    readonly_fields = ['subtotal', 'tax_amount', 'discount_amount', 'total', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline, PaymentInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'description', 'quantity', 'unit_price', 'total']
    list_filter = ['invoice']
    search_fields = ['description']
    readonly_fields = ['total']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'amount', 'method', 'payment_date', 'reference_number']
    list_filter = ['method', 'payment_date']
    search_fields = ['invoice__invoice_number', 'reference_number', 'notes']
    readonly_fields = ['created_at']
