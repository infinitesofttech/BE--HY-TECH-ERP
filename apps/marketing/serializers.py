from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Campaign, CampaignAttachment

User = get_user_model()

AUDIENCE_CHOICES = ['customers', 'leads', 'subscribers']


def get_target_audience_details(obj):
    return list(obj.target_audience or [])


def validate_target_audience(value):
    value = value or []
    for item in value:
        if item not in AUDIENCE_CHOICES:
            raise serializers.ValidationError(
                f"Invalid audience '{item}'. Choose from customers, leads, subscribers."
            )
    return value


class CampaignAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignAttachment
        fields = ['id', 'campaign', 'file', 'name']


class CampaignListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    target_audience_details = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'type', 'name', 'subject', 'status', 'scheduled_at',
            'sent_at', 'created_at', 'created_by', 'created_by_name',
            'deal_value', 'currency', 'period', 'period_value',
            'target_audience', 'target_audience_details',
            'description', 'attachment',
            'stats_sent_count', 'stats_opened_count', 'stats_clicked_count',
            'is_active',
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return ''

    def get_target_audience_details(self, obj):
        return get_target_audience_details(obj)


class CampaignDetailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    target_audience_details = serializers.SerializerMethodField()
    target_audience = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )
    attachments = CampaignAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'type', 'name', 'subject', 'title', 'message', 'content',
            'recipient_filter', 'status', 'scheduled_at', 'sent_at',
            'deal_value', 'currency', 'period', 'period_value',
            'target_audience', 'target_audience_details',
            'description', 'attachment',
            'stats_sent_count', 'stats_opened_count', 'stats_clicked_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'is_active', 'attachments',
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return ''

    def get_target_audience_details(self, obj):
        return get_target_audience_details(obj)

    def validate_target_audience(self, value):
        return validate_target_audience(value)


class CampaignCreateSerializer(serializers.ModelSerializer):
    target_audience = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )

    class Meta:
        model = Campaign
        fields = [
            'type', 'name', 'subject', 'title', 'message', 'content',
            'recipient_filter', 'status', 'scheduled_at',
            'deal_value', 'currency', 'period', 'period_value',
            'target_audience', 'description', 'attachment',
        ]

    def validate_target_audience(self, value):
        return validate_target_audience(value)

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
