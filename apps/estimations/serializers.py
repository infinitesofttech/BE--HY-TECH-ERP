from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers
from .models import Estimation, EstimationItem, Proposal


class EstimationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimationItem
        fields = ['id', 'estimation', 'description', 'quantity', 'unit_price', 'total']
        read_only_fields = ['id', 'total']


class EstimationItemCreateSerializer(serializers.Serializer):
    description = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)


class EstimationSerializer(serializers.ModelSerializer):
    items = EstimationItemSerializer(many=True, read_only=True)
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Estimation
        fields = [
            'id', 'estimation_number', 'title', 'customer_name', 'customer_email',
            'customer_phone', 'valid_until', 'subtotal', 'tax',
            'tax_name', 'tax_percentage',
            'tax_amount', 'discount_percentage', 'discount_amount', 'total',
            'status', 'notes', 'created_by', 'created_at', 'updated_at', 'items',
        ]
        read_only_fields = ['id', 'estimation_number', 'created_by', 'created_at', 'updated_at']

    def _calculate_estimation(self, estimation, items_data):
        subtotal = 0
        item_objs = []
        for item_data in items_data:
            quantity = item_data.get('quantity', 1)
            unit_price = item_data.get('unit_price', 0)
            item_total = quantity * unit_price
            subtotal += item_total
            item_objs.append(EstimationItem(
                estimation=estimation,
                description=item_data['description'],
                quantity=quantity,
                unit_price=unit_price,
                total=item_total,
            ))
        if item_objs:
            EstimationItem.objects.bulk_create(item_objs)

        estimation.subtotal = subtotal
        tax_amount = subtotal * (estimation.tax_percentage / Decimal('100'))
        discount_amount = subtotal * (estimation.discount_percentage / Decimal('100'))
        estimation.tax_amount = tax_amount
        estimation.discount_amount = discount_amount
        estimation.total = subtotal + tax_amount - discount_amount
        estimation.save(update_fields=['subtotal', 'tax_amount', 'discount_amount', 'total'])

    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        estimation = Estimation.objects.create(**validated_data)

        if items_data:
            self._calculate_estimation(estimation, items_data)

        return estimation

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items_data', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            self._calculate_estimation(instance, items_data)
        else:
            instance.subtotal = instance.items.aggregate(total=Sum('total'))['total'] or Decimal('0')
            instance.tax_amount = instance.subtotal * (instance.tax_percentage / Decimal('100'))
            instance.discount_amount = instance.subtotal * (instance.discount_percentage / Decimal('100'))
            instance.total = instance.subtotal + instance.tax_amount - instance.discount_amount
            instance.save(update_fields=['subtotal', 'tax_amount', 'discount_amount', 'total'])

        return instance


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = [
            'id', 'proposal_number', 'title', 'customer_name', 'customer_email',
            'customer_phone', 'content', 'version', 'status', 'valid_until',
            'total_amount', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'proposal_number', 'version', 'created_by', 'created_at', 'updated_at']


class ProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = [
            'title', 'customer_name', 'customer_email', 'customer_phone',
            'content', 'status', 'valid_until', 'total_amount',
        ]
