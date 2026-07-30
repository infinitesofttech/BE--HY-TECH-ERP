from rest_framework import serializers
from .models import Company, Contact


class CompanySerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return obj.owner.email if obj.owner else None


class ContactSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return obj.owner.email if obj.owner else None

    def get_company_name(self, obj):
        return obj.company.name if obj.company else None
