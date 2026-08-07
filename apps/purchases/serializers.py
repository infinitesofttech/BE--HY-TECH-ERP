from decimal import Decimal

from rest_framework import serializers
from .models import (
    Vendor,
    Purchase, PurchaseItem,
    PurchaseOrder, PurchaseOrderItem,
    PurchaseReturn, PurchaseReturnItem,
)


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone', 'country',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PurchaseItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = PurchaseItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price',
            'discount', 'amount', 'note',
        ]
        read_only_fields = ['id', 'amount']


class PurchaseItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'unit_price', 'discount', 'note']


class PurchaseSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    requestor_name = serializers.SerializerMethodField()
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    items = PurchaseItemSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id', 'purchase_id', 'vendor', 'vendor_name', 'requestor',
            'requestor_name', 'company_logo', 'company_from', 'company_to',
            'reference', 'date', 'payment_terms', 'status', 'tax',
            'tax_name', 'tax_percentage',
            'total_discount', 'shipping_charge', 'total_amount', 'notes',
            'terms_conditions', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'purchase_id', 'total_amount', 'created_at', 'updated_at',
        ]

    def get_requestor_name(self, obj):
        if obj.requestor:
            return obj.requestor.get_full_name() or obj.requestor.email
        return ''


class PurchaseCreateSerializer(serializers.ModelSerializer):
    items = PurchaseItemCreateSerializer(many=True, required=True)

    class Meta:
        model = Purchase
        fields = [
            'id', 'vendor', 'requestor', 'company_logo', 'company_from',
            'company_to', 'reference', 'date', 'payment_terms', 'status',
            'tax', 'total_discount', 'shipping_charge', 'notes',
            'terms_conditions', 'items',
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
        purchase = Purchase.objects.create(**validated_data)

        item_objs = []
        for item_data in items_data:
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            discount = item_data.get('discount', 0)
            amount = (quantity * unit_price) - discount
            item_objs.append(PurchaseItem(
                purchase=purchase,
                amount=amount,
                **item_data,
            ))

        PurchaseItem.objects.bulk_create(item_objs)
        purchase.recalculate_total()
        return purchase


class PurchaseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = [
            'vendor', 'requestor', 'company_logo', 'company_from',
            'company_to', 'reference', 'date', 'payment_terms', 'status',
            'tax', 'total_discount', 'shipping_charge', 'notes',
            'terms_conditions',
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.recalculate_total()
        return instance


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price',
            'discount', 'amount', 'note',
        ]
        read_only_fields = ['id', 'amount']


class PurchaseOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity', 'unit_price', 'discount', 'note']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    lead_time_days = serializers.SerializerMethodField()
    on_time = serializers.SerializerMethodField()
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'purchase_order_id', 'vendor', 'vendor_name',
            'company_logo', 'company_from', 'company_to', 'reference',
            'order_date', 'expected_delivery_date', 'actual_delivery_date',
            'lead_time_days', 'on_time', 'payment_terms', 'status', 'tax',
            'tax_name', 'tax_percentage',
            'total_discount', 'shipping_charge', 'total_amount', 'notes',
            'terms_conditions', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'purchase_order_id', 'total_amount', 'created_at',
            'updated_at',
        ]

    def get_lead_time_days(self, obj):
        if obj.actual_delivery_date and obj.order_date:
            return (obj.actual_delivery_date - obj.order_date).days
        if obj.expected_delivery_date and obj.order_date:
            return (obj.expected_delivery_date - obj.order_date).days
        return ''

    def get_on_time(self, obj):
        if (
            obj.actual_delivery_date
            and obj.expected_delivery_date
        ):
            return obj.actual_delivery_date <= obj.expected_delivery_date
        return ''


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemCreateSerializer(many=True, required=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'vendor', 'company_logo', 'company_from', 'company_to',
            'reference', 'order_date', 'expected_delivery_date',
            'actual_delivery_date', 'payment_terms', 'status', 'tax',
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
        order = PurchaseOrder.objects.create(**validated_data)

        item_objs = []
        for item_data in items_data:
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            discount = item_data.get('discount', 0)
            amount = (quantity * unit_price) - discount
            item_objs.append(PurchaseOrderItem(
                purchase_order=order,
                amount=amount,
                **item_data,
            ))

        PurchaseOrderItem.objects.bulk_create(item_objs)
        order.recalculate_total()
        return order


class PurchaseOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = [
            'vendor', 'company_logo', 'company_from', 'company_to',
            'reference', 'order_date', 'expected_delivery_date',
            'actual_delivery_date', 'payment_terms', 'status', 'tax',
            'total_discount', 'shipping_charge', 'notes', 'terms_conditions',
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.recalculate_total()
        return instance


class PurchaseReturnItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = PurchaseReturnItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price',
            'discount', 'amount', 'note',
        ]
        read_only_fields = ['id', 'amount']


class PurchaseReturnItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseReturnItem
        fields = ['product', 'quantity', 'unit_price', 'discount', 'note']


class PurchaseReturnSerializer(serializers.ModelSerializer):
    purchase_id_ref = serializers.CharField(
        source='purchase.purchase_id', read_only=True, default='',
    )
    vendor_name = serializers.CharField(source='vendor.name', read_only=True, default='')
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    items = PurchaseReturnItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseReturn
        fields = [
            'id', 'return_id', 'purchase', 'purchase_id_ref', 'vendor',
            'vendor_name', 'company_logo', 'company_from', 'company_to',
            'reference', 'return_date', 'status', 'return_reason', 'tax',
            'tax_name', 'tax_percentage',
            'total_discount', 'shipping_charge', 'total_amount', 'notes',
            'terms_conditions', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'return_id', 'total_amount', 'created_at', 'updated_at',
        ]


class PurchaseReturnCreateSerializer(serializers.ModelSerializer):
    items = PurchaseReturnItemCreateSerializer(many=True, required=True)

    class Meta:
        model = PurchaseReturn
        fields = [
            'id', 'purchase', 'vendor', 'company_logo', 'company_from',
            'company_to', 'reference', 'return_date', 'status',
            'return_reason', 'tax', 'total_discount', 'shipping_charge',
            'notes', 'terms_conditions', 'items',
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
        purchase_return = PurchaseReturn.objects.create(**validated_data)

        item_objs = []
        for item_data in items_data:
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            discount = item_data.get('discount', 0)
            amount = (quantity * unit_price) - discount
            item_objs.append(PurchaseReturnItem(
                purchase_return=purchase_return,
                amount=amount,
                **item_data,
            ))

        PurchaseReturnItem.objects.bulk_create(item_objs)
        purchase_return.recalculate_total()
        return purchase_return


class PurchaseReturnUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseReturn
        fields = [
            'purchase', 'vendor', 'company_logo', 'company_from',
            'company_to', 'reference', 'return_date', 'status',
            'return_reason', 'tax', 'total_discount', 'shipping_charge',
            'notes', 'terms_conditions',
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.recalculate_total()
        return instance
