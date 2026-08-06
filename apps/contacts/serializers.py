from rest_framework import serializers
from .models import Company, Contact, ContactMessage


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
    visible_to_names = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.email if obj.owner else None

    def get_company_name(self, obj):
        return obj.company.name if obj.company else None

    def get_visible_to_names(self, obj):
        return [
            user.get_full_name() or user.email
            for user in obj.visible_to.all()
        ]


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
