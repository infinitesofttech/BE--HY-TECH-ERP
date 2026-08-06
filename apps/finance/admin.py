from django.contrib import admin

from .models import (
    BankAccount,
    ExpenseCategory, Expense,
    Payment,
    Cashflow,
    Budget,
    Tax,
    IncomeCategory, Income,
    PurchaseTax,
    Payroll,
)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_holder_name', 'account_number', 'account_type', 'is_default', 'is_active')
    list_filter = ('account_type', 'is_default', 'is_active')
    search_fields = ('bank_name', 'account_holder_name', 'account_number')


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'description')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_id', 'name', 'category', 'amount', 'payment_method', 'date', 'status')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('expense_id', 'name', 'description')
    readonly_fields = ('expense_id',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'payee', 'bank', 'payment_method', 'amount', 'date', 'status')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('payment_id', 'payee')
    readonly_fields = ('payment_id',)


@admin.register(Cashflow)
class CashflowAdmin(admin.ModelAdmin):
    list_display = ('ref_id', 'bank', 'type', 'payment_method', 'amount', 'date', 'status')
    list_filter = ('type', 'status', 'payment_method', 'date')
    search_fields = ('ref_id',)
    readonly_fields = ('ref_id',)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('budget_id', 'period', 'category', 'budget', 'status_display')
    list_filter = ('period', 'category')
    search_fields = ('budget_id',)
    readonly_fields = ('budget_id',)

    @admin.display(description='Status')
    def status_display(self, obj):
        return f'{obj.spent()} spent / {obj.remaining()} remaining ({obj.usage_percent()}%)'


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_id', 'name', 'rate', 'status', 'applied_to')
    list_filter = ('status', 'applied_to')
    search_fields = ('tax_id', 'name')
    readonly_fields = ('tax_id',)


@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'description')


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('income_id', 'party_name', 'category', 'amount', 'payment_method', 'date', 'status')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('income_id', 'party_name')
    readonly_fields = ('income_id',)


@admin.register(PurchaseTax)
class PurchaseTaxAdmin(admin.ModelAdmin):
    list_display = ('bill_id', 'supplier', 'tax_type', 'tax_amount', 'payment_method', 'date', 'status')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('bill_id', 'supplier')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = (
        'payroll_id', 'employee', 'designation', 'department',
        'payroll_month', 'payment_date', 'net_salary', 'status',
    )
    list_filter = ('status', 'payroll_month', 'payment_date')
    search_fields = ('payroll_id', 'employee__email', 'employee__first_name')
    readonly_fields = ('payroll_id', 'total_earning', 'total_deduction', 'net_salary')
