from decimal import Decimal

from rest_framework import serializers
from .models import (
    Customer, SalesOrder, SalesOrderItem,
    Refund, DeliveryNote, DeliveryNoteItem,
    CustomerFeedback,
)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'country',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerFeedbackSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = CustomerFeedback
        fields = [
            'id', 'customer', 'customer_name', 'subject', 'feedback',
            'date', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SalesOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = SalesOrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price',
            'discount', 'amount', 'tax', 'tax_name', 'tax_percentage',
            'tax_amount',
        ]
        read_only_fields = ['id', 'amount', 'tax_amount']


class SalesOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = ['product', 'quantity', 'unit_price', 'discount', 'tax']


class SalesOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    employee_name = serializers.SerializerMethodField()
    quotation_id_ref = serializers.CharField(
        source='quotation.quote_id', read_only=True, default='',
    )
    items = SalesOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = SalesOrder
        fields = [
            'id', 'order_id', 'quotation', 'quotation_id_ref', 'employee',
            'employee_name', 'customer', 'customer_name', 'company_logo',
            'company_from', 'company_to', 'date', 'payment_method', 'status',
            'total_discount', 'shipping_charge', 'total_amount', 'notes',
            'terms_conditions', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'order_id', 'total_amount', 'created_at', 'updated_at',
        ]

    def get_employee_name(self, obj):
        if obj.employee:
            return obj.employee.get_full_name() or obj.employee.email
        return ''


class SalesOrderCreateSerializer(serializers.ModelSerializer):
    items = SalesOrderItemCreateSerializer(many=True, required=True)

    class Meta:
        model = SalesOrder
        fields = [
            'id', 'quotation', 'employee', 'customer', 'company_logo',
            'company_from', 'company_to', 'date', 'payment_method', 'status',
            'total_discount', 'shipping_charge', 'notes', 'terms_conditions',
            'items',
        ]
        read_only_fields = ['id']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one item is required.')
        for item in value:
            if item.get('quantity', 0) <= 0:
                raise serializers.ValidationError(
                    'Quantity must be greater than zero.',
                )
            if item.get('unit_price', 0) <= 0:
                raise serializers.ValidationError(
                    'Unit price must be greater than zero.',
                )
            if item.get('discount', 0) < 0:
                raise serializers.ValidationError(
                    'Discount cannot be negative.',
                )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = SalesOrder.objects.create(**validated_data)

        item_objs = []
        for item_data in items_data:
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            discount = item_data.get('discount', 0)
            tax = item_data.get('tax')
            tax_rate = tax.rate if tax else 0
            amount = (quantity * unit_price) - discount
            tax_amount = amount * tax_rate / Decimal('100')
            item_objs.append(SalesOrderItem(
                order=order,
                amount=amount,
                tax_amount=tax_amount,
                **item_data,
            ))

        SalesOrderItem.objects.bulk_create(item_objs)
        order.recalculate_total()
        return order


class SalesOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = [
            'employee', 'customer', 'company_logo', 'company_from', 'company_to',
            'date', 'payment_method', 'status', 'total_discount',
            'shipping_charge', 'notes', 'terms_conditions',
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.recalculate_total()
        return instance


class RefundSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'refund_id', 'reference', 'amount', 'customer',
            'customer_name', 'payment_method', 'status', 'refund_reason',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'refund_id', 'created_at', 'updated_at']


class DeliveryNoteItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = DeliveryNoteItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price',
            'discount', 'amount', 'note',
        ]
        read_only_fields = ['id', 'amount']


class DeliveryNoteItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryNoteItem
        fields = ['product', 'quantity', 'unit_price', 'discount', 'note']


class DeliveryNoteSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    sales_order_id_ref = serializers.CharField(
        source='sales_order.order_id', read_only=True, default='',
    )
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    items = DeliveryNoteItemSerializer(many=True, read_only=True)

    class Meta:
        model = DeliveryNote
        fields = [
            'id', 'delivery_note_id', 'sales_order', 'sales_order_id_ref',
            'customer', 'customer_name', 'company_logo', 'company_from',
            'company_to', 'reference', 'invoice_date', 'due_date', 'frequency',
            'status', 'note', 'terms_conditions', 'tax', 'tax_name',
            'tax_percentage', 'total_discount', 'shipping_charge',
            'total_amount', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'delivery_note_id', 'total_amount', 'created_at', 'updated_at',
        ]


class DeliveryNoteCreateSerializer(serializers.ModelSerializer):
    items = DeliveryNoteItemCreateSerializer(many=True, required=True)

    class Meta:
        model = DeliveryNote
        fields = [
            'id', 'sales_order', 'customer', 'company_logo', 'company_from',
            'company_to', 'reference', 'invoice_date', 'due_date', 'frequency',
            'status', 'note', 'terms_conditions', 'tax', 'total_discount',
            'shipping_charge', 'items',
        ]
        read_only_fields = ['id']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one item is required.')
        for item in value:
            if item.get('quantity', 0) <= 0:
                raise serializers.ValidationError(
                    'Quantity must be greater than zero.',
                )
            if item.get('unit_price', 0) <= 0:
                raise serializers.ValidationError(
                    'Unit price must be greater than zero.',
                )
            if item.get('discount', 0) < 0:
                raise serializers.ValidationError(
                    'Discount cannot be negative.',
                )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        delivery_note = DeliveryNote.objects.create(**validated_data)

        item_objs = []
        for item_data in items_data:
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            discount = item_data.get('discount', 0)
            amount = (quantity * unit_price) - discount
            item_objs.append(DeliveryNoteItem(
                delivery_note=delivery_note,
                amount=amount,
                **item_data,
            ))

        DeliveryNoteItem.objects.bulk_create(item_objs)
        delivery_note.recalculate_total()
        return delivery_note


class DeliveryNoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryNote
        fields = [
            'customer', 'company_logo', 'company_from', 'company_to',
            'reference', 'invoice_date', 'due_date', 'frequency', 'status',
            'note', 'terms_conditions', 'tax', 'total_discount',
            'shipping_charge',
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.recalculate_total()
        return instance
