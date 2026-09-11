from rest_framework import serializers

from .models import Payroll, Expense


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_role = serializers.CharField(source='employee.role', read_only=True)

    class Meta:
        model = Payroll
        fields = [
            'id', 'payroll_no', 'employee', 'employee_name', 'employee_role',
            'payroll_month', 'basic_pay', 'hra', 'allowances', 'pf',
            'net_monthly', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'payroll_no', 'net_monthly', 'created_at', 'updated_at']

    def get_employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username

    def validate_hra(self, value):
        basic = self.initial_data.get('basic_pay')
        try:
            basic = float(basic) if basic else 0
        except (TypeError, ValueError):
            basic = 0
        if value == 0 and basic:
            return round(basic * 0.20, 2)
        return value


class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    payment_mode_display = serializers.CharField(source='get_payment_mode_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            'id', 'expense_no', 'expense_name', 'category', 'category_display',
            'payment_mode', 'payment_mode_display', 'amount', 'note',
            'expense_date', 'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'expense_no', 'created_by_name', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return ''
