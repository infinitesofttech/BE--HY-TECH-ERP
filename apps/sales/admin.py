from django.contrib import admin
from .models import SalesReport, SalesReportItem


class SalesReportItemInline(admin.TabularInline):
    model = SalesReportItem
    extra = 1
    readonly_fields = ['total']


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'dealer', 'date', 'total_revenue',
        'total_items', 'created_at',
    ]
    list_filter = ['date', 'employee', 'dealer']
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'dealer__name', 'notes',
    ]
    readonly_fields = ['total_revenue', 'total_items', 'created_at', 'updated_at']
    inlines = [SalesReportItemInline]


@admin.register(SalesReportItem)
class SalesReportItemAdmin(admin.ModelAdmin):
    list_display = ['report', 'product', 'quantity', 'unit_price', 'total']
    list_filter = ['product']
    readonly_fields = ['total']
