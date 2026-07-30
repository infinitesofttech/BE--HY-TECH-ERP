from rest_framework import serializers
from .models import Campaign, CampaignAttachment


class CampaignAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignAttachment
        fields = ['id', 'campaign', 'file', 'name']


class CampaignListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'type', 'name', 'status', 'scheduled_at',
            'sent_at', 'created_at', 'created_by', 'created_by_name',
            'stats_sent_count', 'stats_opened_count', 'stats_clicked_count',
            'is_active',
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return ''


class CampaignDetailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    attachments = CampaignAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'type', 'name', 'subject', 'title', 'message', 'content',
            'recipient_filter', 'status', 'scheduled_at', 'sent_at',
            'stats_sent_count', 'stats_opened_count', 'stats_clicked_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'is_active', 'attachments',
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return ''


class CampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            'type', 'name', 'subject', 'title', 'message', 'content',
            'recipient_filter', 'status', 'scheduled_at',
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
