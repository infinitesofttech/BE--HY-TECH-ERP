from django.contrib import admin
from .models import Order, OrderItem, Quotation, QuotationItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'dealer', 'client', 'order_date', 'total_amount', 'net_amount', 'payment_status', 'status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['employee__first_name', 'employee__last_name', 'dealer__name', 'client']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'unit_price', 'total']
    list_filter = ['product']
    readonly_fields = ['total']


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 0
    readonly_fields = ['amount']


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quote_id', 'client', 'quote_date', 'valid_till', 'total_amount', 'discount', 'final_amount', 'status', 'created_at']
    list_filter = ['status', 'quote_date']
    search_fields = ['quote_id', 'client']
    readonly_fields = ['quote_id', 'total_amount', 'final_amount', 'created_at', 'updated_at']
    inlines = [QuotationItemInline]


@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'quotation', 'product', 'quantity', 'price', 'discount', 'amount']
    readonly_fields = ['amount']
