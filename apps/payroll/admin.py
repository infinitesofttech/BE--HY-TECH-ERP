from django.contrib import admin
from .models import Payroll, Expense


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'payroll_no', 'employee', 'payroll_month', 'basic_pay',
        'hra', 'allowances', 'pf', 'net_monthly', 'status', 'created_at',
    ]
    list_filter = ['payroll_month', 'status']
    search_fields = ['payroll_no', 'employee__username', 'employee__email']
    readonly_fields = ['payroll_no', 'net_monthly', 'created_at', 'updated_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'expense_no', 'expense_name', 'category', 'payment_mode',
        'amount', 'expense_date', 'created_by', 'created_at',
    ]
    list_filter = ['category', 'payment_mode']
    search_fields = ['expense_no', 'expense_name', 'note']
    readonly_fields = ['expense_no', 'created_at', 'updated_at']
