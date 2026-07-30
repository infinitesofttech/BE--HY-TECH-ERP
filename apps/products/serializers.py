from rest_framework import serializers
from .models import ProductCategory, Product, TourPlan, Policy


class ProductCategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'description', 'is_active',
            'product_count', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'description',
            'specifications', 'sku', 'cost_price', 'selling_price', 'price',
            'tax_percentage', 'unit', 'quantity', 'image', 'for_vehicle_type',
            'status', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'description', 'specifications',
            'sku', 'cost_price', 'selling_price', 'price',
            'tax_percentage', 'unit', 'quantity', 'image', 'for_vehicle_type',
            'status', 'is_active',
        ]
        read_only_fields = ['id']


class ProductCatalogueSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category_name', 'description', 'specifications',
            'sku', 'cost_price', 'selling_price', 'price',
            'tax_percentage', 'unit', 'quantity', 'image', 'for_vehicle_type',
            'status',
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
