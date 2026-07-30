from rest_framework import serializers
from .models import Contract


class ContractSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = '__all__'

    def get_created_by_name(self, obj):
        return obj.created_by.email if obj.created_by else None
