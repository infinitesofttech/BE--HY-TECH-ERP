from rest_framework import serializers
from decimal import Decimal
from .models import BaseService, SubService, RequiredDocument, Transaction
from apps.hytech_customers.models import Customer


class RequiredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredDocument
        fields = ['id', 'SubService', 'DocumentName', 'document_type', 'IsRequired', 'CreatedAt']
        read_only_fields = ['id', 'CreatedAt']


class SubServiceSerializer(serializers.ModelSerializer):
    RequiredDocuments = RequiredDocumentSerializer(source='required_documents', many=True, read_only=True)
    required_documents = RequiredDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = SubService
        fields = [
            'id', 'Service', 'SubServiceName', 'Description', 'IsActive',
            'CreatedAt', 'UpdatedAt', 'RequiredDocuments', 'required_documents'
        ]
        read_only_fields = ['id', 'CreatedAt', 'UpdatedAt']


class BaseServiceSerializer(serializers.ModelSerializer):
    SubServices = SubServiceSerializer(source='sub_services', many=True, read_only=True)
    sub_services = SubServiceSerializer(many=True, read_only=True)

    class Meta:
        model = BaseService
        fields = [
            'id', 'ServiceName', 'ServiceNameGu', 'Category', 'SubCategory',
            'Department', 'ServiceType', 'Description', 'GovernmentFee',
            'ServiceCharge', 'TotalFee', 'SlaDays', 'Priority',
            'SmsTemplateGu', 'SmsTemplateEn', 'StaffInstructions',
            'FormFields', 'PortalUrl', 'IsOfficial', 'IsActive',
            'CreatedAt', 'UpdatedAt', 'SubServices', 'sub_services'
        ]
        read_only_fields = ['id', 'CreatedAt', 'UpdatedAt']


class TransactionSerializer(serializers.ModelSerializer):
    family_id = serializers.CharField(source='customer.family_id', read_only=True)
    customer_name = serializers.CharField(source='customer.head_of_family', read_only=True)
    service_name = serializers.CharField(source='service.ServiceName', read_only=True, default='')
    sub_service_name = serializers.CharField(source='sub_service.SubServiceName', read_only=True, default='')
    staff_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_no', 'transaction_date', 'customer',
            'service', 'sub_service', 'staff', 'family_id', 'customer_name',
            'service_name', 'sub_service_name', 'staff_name', 'bill_amount',
            'paid_amount', 'due_amount', 'payment_status', 'payment_mode',
            'points_earned', 'employee_points', 'points_redeemed',
            'wallet_credit', 'wallet_used', 'net_wallet_change',
            'previous_due_cleared', 'remarks', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'transaction_no', 'created_at', 'updated_at']

    def get_staff_name(self, obj):
        if obj.staff:
            return obj.staff.get_full_name() or obj.staff.username
        return "Staff Member"

    def create(self, validated_data):
        transaction = super().create(validated_data)
        customer = transaction.customer
        if customer:
            # Update points
            earned = int(transaction.points_earned or 0)
            redeemed = int(transaction.points_redeemed or 0)
            customer.current_points = max(0, customer.current_points + earned - redeemed)

            # Update wallet balance
            credit = Decimal(str(transaction.wallet_credit or 0))
            used = Decimal(str(transaction.wallet_used or 0))
            customer.wallet_balance = Decimal(str(customer.wallet_balance or 0)) + credit - used
            if customer.wallet_balance < 0:
                customer.wallet_balance = Decimal('0.00')

            customer.save(update_fields=['current_points', 'wallet_balance'])

        return transaction
