from rest_framework import serializers

from django.db import transaction

from .models import (
    ProductCategory, Product, TourPlan, Policy, Warehouse, Supplier, Inventory,
    StockAdjustment, StockTransfer,
)


def _lockable_inventory(product, warehouse):
    return Inventory.objects.select_for_update().filter(
        product=product, warehouse=warehouse,
    ).first()


class ProductCategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'status',
            'product_count', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'description',
            'specifications', 'sku', 'cost_price', 'selling_price', 'price',
            'tax', 'tax_name', 'tax_percentage', 'unit', 'quantity', 'image',
            'for_vehicle_type', 'status', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'description', 'specifications',
            'sku', 'cost_price', 'selling_price', 'price',
            'tax', 'unit', 'quantity', 'image', 'for_vehicle_type',
            'status', 'is_active',
        ]
        read_only_fields = ['id']


class ProductCatalogueSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    tax_name = serializers.CharField(source='tax.name', read_only=True, default='')
    tax_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category_name', 'description', 'specifications',
            'sku', 'cost_price', 'selling_price', 'price',
            'tax_name', 'tax_percentage', 'unit', 'quantity', 'image',
            'for_vehicle_type', 'status',
        ]


class TourPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPlan
        fields = [
            'id', 'name', 'description', 'tour_type', 'start_date', 'end_date',
            'duration_days', 'plan_details', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            'id', 'title', 'description', 'category',
            'attachment', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'contact_person', 'phone', 'capacity',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'email', 'phone', 'country',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 'product', 'product_name', 'warehouse', 'warehouse_name',
            'quantity', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockAdjustmentSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = StockAdjustment
        fields = [
            'id', 'product', 'product_name', 'warehouse', 'warehouse_name',
            'reason', 'difference', 'adjustment_date', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_difference(self, value):
        if value == 0:
            raise serializers.ValidationError('Difference cannot be zero.')
        return value

    def validate(self, attrs):
        if 'difference' in attrs and attrs['difference'] < 0:
            product = attrs.get('product', getattr(self.instance, 'product', None))
            warehouse = attrs.get('warehouse', getattr(self.instance, 'warehouse', None))
            if product and warehouse:
                with transaction.atomic():
                    current = _lockable_inventory(product, warehouse)
                    available = current.quantity if current else 0
                    if available + attrs['difference'] < 0:
                        raise serializers.ValidationError(
                            {'difference': f'Insufficient stock in {warehouse.name}. Available: {available}.'}
                        )
        return attrs


class StockTransferSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    from_warehouse_name = serializers.CharField(
        source='from_warehouse.name', read_only=True,
    )
    to_warehouse_name = serializers.CharField(
        source='to_warehouse.name', read_only=True,
    )

    class Meta:
        model = StockTransfer
        fields = [
            'id', 'product', 'product_name', 'from_warehouse',
            'from_warehouse_name', 'to_warehouse', 'to_warehouse_name',
            'quantity', 'transfer_date', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        from_warehouse = attrs.get('from_warehouse')
        to_warehouse = attrs.get('to_warehouse')
        if from_warehouse and from_warehouse == to_warehouse:
            raise serializers.ValidationError(
                'Source and destination warehouses must be different.'
            )
        if self.instance is not None:
            immutable_fields = ('product', 'from_warehouse', 'to_warehouse', 'quantity')
            for field in immutable_fields:
                if field in attrs and getattr(self.instance, field) != attrs[field]:
                    raise serializers.ValidationError(
                        {field: 'This field cannot be changed after the transfer is created.'}
                    )
        return attrs
