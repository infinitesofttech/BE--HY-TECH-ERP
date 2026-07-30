from rest_framework import serializers
from .models import SalesReport, SalesReportItem


class SalesReportItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SalesReportItem
        fields = [
            'id', 'product', 'product_name', 'quantity',
            'unit_price', 'total',
        ]
        read_only_fields = ['id', 'total']


class SalesReportItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReportItem
        fields = ['product', 'quantity', 'unit_price']


class SalesReportSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    dealer_name = serializers.SerializerMethodField()
    items = SalesReportItemSerializer(many=True, read_only=True)

    class Meta:
        model = SalesReport
        fields = [
            'id', 'employee', 'employee_name', 'dealer', 'dealer_name',
            'date', 'total_revenue', 'total_items', 'notes',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'total_revenue', 'total_items', 'created_at', 'updated_at',
        ]

    def get_employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.email

    def get_dealer_name(self, obj):
        if obj.dealer:
            return obj.dealer.name
        return None


class SalesReportCreateSerializer(serializers.ModelSerializer):
    items = SalesReportItemCreateSerializer(many=True, required=True)

    class Meta:
        model = SalesReport
        fields = [
            'id', 'employee', 'dealer', 'date', 'notes', 'items',
        ]
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
        report = SalesReport.objects.create(**validated_data)

        total_revenue = 0
        total_items = 0
        item_objs = []
        for item_data in items_data:
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            item_total = quantity * unit_price
            total_revenue += item_total
            total_items += quantity
            item_objs.append(SalesReportItem(
                report=report,
                product=item_data['product'],
                quantity=quantity,
                unit_price=unit_price,
                total=item_total,
            ))

        SalesReportItem.objects.bulk_create(item_objs)
        report.total_revenue = total_revenue
        report.total_items = total_items
        report.save(update_fields=['total_revenue', 'total_items'])

        return report
