from django.contrib import admin
from .models import Order, OrderItem


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
