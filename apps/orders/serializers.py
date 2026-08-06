from rest_framework import serializers
from .models import Order, OrderItem, Quotation, QuotationItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity',
            'unit_price', 'total',
        ]
        read_only_fields = ['id', 'total']


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    dealer_name = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'employee', 'employee_name', 'dealer', 'dealer_name',
            'client', 'order_date', 'total_amount', 'net_amount',
            'payment_status', 'status', 'notes', 'items',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'total_amount', 'created_at', 'updated_at',
        ]

    def get_employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.email

    def get_dealer_name(self, obj):
        return obj.dealer.name if obj.dealer else None


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, required=True)

    class Meta:
        model = Order
        fields = ['id', 'employee', 'dealer', 'client', 'order_date', 'notes', 'items']
        read_only_fields = ['id']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                'At least one item is required.',
            )
        for item in value:
            if item.get('quantity', 0) <= 0:
                raise serializers.ValidationError(
                    'Quantity must be greater than zero.',
                )
            if item.get('unit_price', 0) <= 0:
                raise serializers.ValidationError(
                    'Unit price must be greater than zero.',
                )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total_amount = 0
        item_objs = []
        for item_data in items_data:
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            item_total = quantity * unit_price
            total_amount += item_total
            item_objs.append(OrderItem(
                order=order,
                product=item_data['product'],
                quantity=quantity,
                unit_price=unit_price,
                total=item_total,
            ))

        OrderItem.objects.bulk_create(item_objs)
        order.total_amount = total_amount
        order.net_amount = total_amount
        order.save(update_fields=['total_amount', 'net_amount'])

        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        allowed = dict(Order.STATUS_CHOICES).keys()
        if value not in allowed:
            raise serializers.ValidationError(
                f'Invalid status. Allowed: {", ".join(allowed)}',
            )
        return value


class QuotationItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default='')

    class Meta:
        model = QuotationItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'discount', 'amount']
        read_only_fields = ['id', 'amount']


class QuotationItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ['product', 'quantity', 'price', 'discount']


class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    lead_name = serializers.CharField(source='lead.name', read_only=True, default='')
    customer_name = serializers.CharField(source='customer.name', read_only=True, default='')
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Quotation
        fields = [
            'id', 'quote_id', 'client', 'lead', 'lead_name', 'customer',
            'customer_name', 'quote_date', 'valid_till', 'delivery_date',
            'payment_terms', 'tax', 'tax_name', 'tax_percentage',
            'gst_amount', 'shipping_charge',
            'total_amount', 'discount', 'final_amount', 'notes', 'status',
            'created_by', 'created_by_name', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'quote_id', 'gst_amount', 'total_amount', 'final_amount',
            'created_at', 'updated_at',
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.email if obj.created_by else ''


class QuotationCreateSerializer(serializers.ModelSerializer):
    items = QuotationItemCreateSerializer(many=True, required=True)

    class Meta:
        model = Quotation
        fields = [
            'id', 'client', 'lead', 'customer', 'quote_date', 'valid_till',
            'delivery_date', 'payment_terms', 'tax', 'shipping_charge',
            'discount', 'notes', 'status', 'items',
        ]
        read_only_fields = ['id']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one item is required.')
        for item in value:
            if item.get('quantity', 0) <= 0:
                raise serializers.ValidationError('Quantity must be greater than zero.')
            if item.get('price', 0) <= 0:
                raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        quotation = Quotation.objects.create(**validated_data)

        total_amount = 0
        item_objs = []
        for item_data in items_data:
            quantity = item_data['quantity']
            price = item_data['price']
            discount = item_data.get('discount', 0)
            if discount >= 100:
                amount = 0
            else:
                amount = quantity * price * (1 - discount / 100)
            total_amount += amount
            item_objs.append(QuotationItem(
                quotation=quotation,
                product=item_data.get('product'),
                quantity=quantity,
                price=price,
                discount=discount,
                amount=amount,
            ))

        QuotationItem.objects.bulk_create(item_objs)
        quotation.total_amount = total_amount
        quotation.recalculate_totals()

        return quotation
