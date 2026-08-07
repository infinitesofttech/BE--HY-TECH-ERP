from decimal import Decimal

from rest_framework import serializers
from apps.products.models import Product

from .models import Order, OrderItem, Quotation, QuotationItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default='')

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
            'id', 'total_amount', 'net_amount', 'created_at', 'updated_at',
        ]

    def get_employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.email

    def get_dealer_name(self, obj):
        return obj.dealer.name if obj.dealer else ''


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
    lead_name = serializers.CharField(source='lead.name', read_only=True, default='')
    customer_name = serializers.CharField(source='customer.name', read_only=True, default='')

    class Meta:
        model = Quotation
        fields = [
            'id', 'quote_id', 'client', 'lead', 'lead_name', 'customer',
            'customer_name', 'quote_date', 'valid_till', 'delivery_date',
            'payment_terms', 'status', 'total_amount', 'discount',
            'final_amount', 'notes', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'quote_id', 'total_amount', 'final_amount',
            'created_at', 'updated_at',
        ]


class QuotationCreateSerializer(serializers.ModelSerializer):
    items = QuotationItemCreateSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = Quotation
        fields = [
            'id', 'client', 'lead', 'customer', 'quote_date', 'valid_till',
            'delivery_date', 'payment_terms', 'tax', 'shipping_charge',
            'discount', 'notes', 'status', 'items',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        items = attrs.get('items')
        lead = attrs.get('lead')
        if not items and lead:
            product_name = getattr(lead, 'product_requirement', '') or ''
            if product_name:
                product = Product.objects.filter(name__iexact=product_name).first()
                if product is not None:
                    attrs['items'] = [{
                        'product': product,
                        'quantity': getattr(lead, 'quantity', 1) or 1,
                        'price': product.price,
                        'discount': Decimal('0'),
                    }]
        return attrs

    def validate_items(self, value):
        if value is None:
            return []
        for item in value:
            if item.get('quantity', 0) <= 0:
                raise serializers.ValidationError('Quantity must be greater than zero.')
            if item.get('price', 0) <= 0:
                raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def create(self, validated_data, **kwargs):
        items_data = validated_data.pop('items', [])
        lead = validated_data.get('lead')
        if not items_data and lead:
            product_name = getattr(lead, 'product_requirement', '') or ''
            if product_name:
                product = Product.objects.filter(name__iexact=product_name).first()
                if product is not None:
                    items_data = [{
                        'product': product,
                        'quantity': getattr(lead, 'quantity', 1) or 1,
                        'price': product.price,
                        'discount': Decimal('0'),
                    }]

        validated_data['created_by'] = kwargs.get('created_by')
        quotation = Quotation.objects.create(**validated_data)

        total_amount = 0
        item_objs = []
        for item_data in items_data:
            product = item_data.get('product')
            if not isinstance(product, Product):
                product = Product.objects.filter(pk=product).first() if product else None
            quantity = int(item_data['quantity'])
            price = Decimal(str(item_data['price']))
            discount = Decimal(str(item_data.get('discount', 0)))
            if discount >= Decimal('100'):
                amount = Decimal('0')
            else:
                discount_rate = discount / Decimal('100')
                amount = Decimal(quantity) * price * (Decimal('1') - discount_rate)
            total_amount += amount
            item_objs.append(QuotationItem(
                quotation=quotation,
                product=product,
                quantity=quantity,
                price=price,
                discount=discount,
                amount=amount,
            ))

        QuotationItem.objects.bulk_create(item_objs)
        quotation.total_amount = total_amount
        quotation.recalculate_totals()

        return quotation
