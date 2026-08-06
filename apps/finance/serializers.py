from rest_framework import serializers

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


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = [
            'id', 'name', 'slug', 'description', 'status', 'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'expense_id', 'name', 'category', 'category_name', 'amount',
            'payment_method', 'date', 'description', 'status', 'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'expense_id', 'created_at', 'updated_at',
        ]


class PaymentSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.bank_name', read_only=True, default='')

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'payee', 'bank', 'bank_name', 'payment_method',
            'amount', 'date', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'payment_id', 'created_at', 'updated_at']


class CashflowSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.bank_name', read_only=True, default='')

    class Meta:
        model = Cashflow
        fields = [
            'id', 'ref_id', 'bank', 'bank_name', 'type', 'payment_method',
            'amount', 'date', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'ref_id', 'created_at', 'updated_at']


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    usage_percent = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'budget_id', 'period', 'category', 'category_name', 'budget',
            'spent', 'remaining', 'usage_percent', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'budget_id', 'created_at', 'updated_at',
        ]

    def get_spent(self, obj):
        return float(obj.spent())

    def get_remaining(self, obj):
        return float(obj.remaining())

    def get_usage_percent(self, obj):
        return obj.usage_percent()


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = [
            'id', 'tax_id', 'name', 'rate', 'status', 'applied_to',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'tax_id', 'created_at', 'updated_at']


class IncomeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeCategory
        fields = [
            'id', 'name', 'slug', 'description', 'status', 'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class IncomeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Income
        fields = [
            'id', 'income_id', 'party_name', 'category', 'category_name',
            'amount', 'payment_method', 'date', 'status', 'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'income_id', 'created_at', 'updated_at']


class PurchaseTaxSerializer(serializers.ModelSerializer):
    tax_type_name = serializers.CharField(source='tax_type.name', read_only=True, default='')

    class Meta:
        model = PurchaseTax
        fields = [
            'id', 'bill_id', 'supplier', 'tax_type', 'tax_type_name',
            'tax_amount', 'payment_method', 'date', 'status', 'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    designation_name = serializers.CharField(
        source='designation.name', read_only=True, default='',
    )
    department_name = serializers.CharField(
        source='department.name', read_only=True, default='',
    )

    class Meta:
        model = Payroll
        fields = [
            'id', 'payroll_id', 'employee', 'employee_name', 'designation',
            'designation_name', 'department', 'department_name',
            'payroll_month', 'payment_date', 'basic_salary', 'hra',
            'conveyance', 'bonus', 'other_allowance', 'pf', 'professional_tax',
            'tds', 'other_deductions', 'total_earning', 'total_deduction',
            'net_salary', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'payroll_id', 'total_earning', 'total_deduction',
            'net_salary', 'created_at', 'updated_at',
        ]

    def get_employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.email

    def create(self, validated_data):
        employee = validated_data.get('employee')
        if employee:
            validated_data.setdefault('designation', employee.designation)
            validated_data.setdefault('department', employee.department)
        return Payroll.objects.create(**validated_data)
