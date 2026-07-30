from rest_framework import serializers
from .models import EmailTemplate, EmailCampaign


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = '__all__'


class EmailCampaignSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailCampaign
        fields = '__all__'

    def get_created_by_name(self, obj):
        return obj.created_by.email if obj.created_by else ''
