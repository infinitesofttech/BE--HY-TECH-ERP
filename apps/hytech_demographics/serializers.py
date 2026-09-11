from rest_framework import serializers
from .models import Village, ContactInquiry, AuditLog


class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = [
            'id', 'code', 'name', 'name_gu', 'taluka', 'district',
            'total_families', 'total_citizens', 'total_documents',
            'male_count', 'female_count', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'code', 'created_at']


class ContactInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = [
            'id', 'full_name', 'mobile_number', 'email', 'subject',
            'service_interest', 'message', 'status', 'assigned_to',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'id', 'timestamp', 'user_name', 'user_role', 'action',
            'entity_type', 'entity_id', 'details', 'ip_address'
        ]
        read_only_fields = ['id', 'timestamp']
