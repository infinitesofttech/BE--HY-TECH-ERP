from rest_framework import serializers

from .models import (
    AssetRegistration,
    AssetAssignment,
    AssetDepreciation,
    AssetMaintenance,
    AssetDisposal,
)


class AssetRegistrationSerializer(serializers.ModelSerializer):
    asset_user_name = serializers.CharField(
        source='asset_user.get_full_name', read_only=True, default='',
    )

    class Meta:
        model = AssetRegistration
        fields = [
            'id', 'asset_name', 'asset_user', 'asset_user_name', 'category',
            'location', 'purchase_date', 'warranty_end_date', 'warranty',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'asset_user_name', 'created_at', 'updated_at']


class AssetAssignmentSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.asset_name', read_only=True)
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name', read_only=True, default='',
    )

    class Meta:
        model = AssetAssignment
        fields = [
            'id', 'assignment_id', 'asset', 'asset_name', 'assigned_to',
            'assigned_to_name', 'department', 'assignment_date', 'return_date',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'assignment_id', 'asset_name', 'assigned_to_name', 'created_at', 'updated_at']


class AssetDepreciationSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.asset_name', read_only=True)

    class Meta:
        model = AssetDepreciation
        fields = [
            'id', 'depreciation_id', 'asset', 'asset_name', 'purchase_cost',
            'accumulated_depreciation', 'net_book_value', 'depreciation_method',
            'useful_life_years', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'depreciation_id', 'asset_name', 'created_at', 'updated_at']


class AssetMaintenanceSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.asset_name', read_only=True)

    class Meta:
        model = AssetMaintenance
        fields = [
            'id', 'maintenance_id', 'asset', 'asset_name', 'maintenance_type',
            'scheduled_date', 'remark', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'maintenance_id', 'asset_name', 'created_at', 'updated_at']


class AssetDisposalSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.asset_name', read_only=True)
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name', read_only=True, default='',
    )

    class Meta:
        model = AssetDisposal
        fields = [
            'id', 'disposal_id', 'asset', 'asset_name', 'method', 'value',
            'date', 'approved_by', 'approved_by_name', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'disposal_id', 'asset_name', 'approved_by_name', 'created_at', 'updated_at']


class AssetAnalyticsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    asset_name = serializers.CharField()
    category = serializers.CharField()
    purchase_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    current_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    depreciation = serializers.DecimalField(max_digits=12, decimal_places=2)
    location = serializers.CharField()
    assigned_to = serializers.CharField()
    status = serializers.CharField()
