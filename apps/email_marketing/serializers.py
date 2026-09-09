from rest_framework import serializers
from .models import EmailTemplate, EmailCampaign, SubscriberList


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = '__all__'


class EmailCampaignSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailCampaign
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_created_by_name(self, obj):
        return obj.created_by.email if obj.created_by else ''


class SubscriberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriberList
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailEngagementSerializer(serializers.ModelSerializer):
    engagement_rate = serializers.SerializerMethodField()

    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'name', 'campaign_type', 'period', 'status',
            'sent_count', 'opened_count', 'clicked_count', 'engagement_rate',
            'created_at',
        ]

    def get_engagement_rate(self, obj):
        if obj.sent_count > 0:
            return round(((obj.opened_count + obj.clicked_count) / obj.sent_count) * 100, 2)
        return 0
