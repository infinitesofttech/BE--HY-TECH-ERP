from rest_framework import serializers

from .models import BankAccount, PurchaseTransaction, PaymentGateway, DiscountRule


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class BankAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'bank_name', 'account_holder_name', 'account_number',
            'ifsc_code', 'branch', 'account_type', 'is_default', 'is_active',
        ]


class PurchaseTransactionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PurchaseTransaction
        fields = '__all__'
        read_only_fields = ['id', 'transaction_id', 'created_by', 'created_at']


class PurchaseTransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseTransaction
        fields = [
            'vendor_name', 'invoice_number', 'amount', 'tax_amount',
            'total_amount', 'payment_method', 'payment_date', 'status', 'notes',
        ]


class PaymentGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGateway
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        secret = data.get('api_secret', '')
        if secret and len(secret) > 8:
            data['api_secret'] = secret[:4] + '*' * (len(secret) - 8) + secret[-4:]
        elif secret:
            data['api_secret'] = '****'
        return data


class DiscountRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountRule
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class DiscountRuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountRule
        fields = [
            'name', 'type', 'value', 'min_order_amount',
            'max_discount_amount', 'applicable_to', 'is_active',
            'valid_from', 'valid_until',
        ]
