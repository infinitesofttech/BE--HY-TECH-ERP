from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'invoice', 'description', 'quantity', 'unit_price', 'total']
        read_only_fields = ['id', 'total']


class InvoiceItemCreateSerializer(serializers.Serializer):
    description = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    sales_order_id_ref = serializers.CharField(
        source='sales_order.order_id', read_only=True, default='',
    )
    delivery_note_id_ref = serializers.CharField(
        source='delivery_note.delivery_note_id', read_only=True, default='',
    )

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'sales_order', 'sales_order_id_ref',
            'delivery_note', 'delivery_note_id_ref',
            'customer_name', 'customer_email',
            'customer_address', 'billing_address', 'invoice_date', 'due_date',
            'payment_method', 'transaction_id', 'subtotal', 'tax',
            'tax_name', 'tax_percentage',
            'tax_amount', 'discount_percentage', 'discount_amount', 'total',
            'status', 'notes', 'terms_conditions', 'created_by',
            'created_at', 'updated_at', 'items',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def _calculate_invoice(self, invoice, items_data):
        subtotal = 0
        item_objs = []
        for item_data in items_data:
            quantity = item_data.get('quantity', 1)
            unit_price = item_data.get('unit_price', 0)
            item_total = quantity * unit_price
            subtotal += item_total
            item_objs.append(InvoiceItem(
                invoice=invoice,
                description=item_data['description'],
                quantity=quantity,
                unit_price=unit_price,
                total=item_total,
            ))
        if item_objs:
            InvoiceItem.objects.bulk_create(item_objs)

        invoice.subtotal = subtotal
        tax_amount = subtotal * (invoice.tax_percentage / Decimal('100'))
        discount_amount = subtotal * (invoice.discount_percentage / Decimal('100'))
        invoice.tax_amount = tax_amount
        invoice.discount_amount = discount_amount
        invoice.total = subtotal + tax_amount - discount_amount
        invoice.save(update_fields=['subtotal', 'tax_amount', 'discount_amount', 'total'])

    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        invoice = Invoice.objects.create(**validated_data)

        if items_data:
            self._calculate_invoice(invoice, items_data)

        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items_data', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            self._calculate_invoice(instance, items_data)
        else:
            instance.subtotal = instance.items.aggregate(total=Sum('total'))['total'] or Decimal('0')
            instance.tax_amount = instance.subtotal * (instance.tax_percentage / Decimal('100'))
            instance.discount_amount = instance.subtotal * (instance.discount_percentage / Decimal('100'))
            instance.total = instance.subtotal + instance.tax_amount - instance.discount_amount
            instance.save(update_fields=['subtotal', 'tax_amount', 'discount_amount', 'total'])

        return instance


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'amount', 'method', 'payment_date',
            'reference_number', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
