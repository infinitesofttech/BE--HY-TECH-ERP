from rest_framework import serializers
from django.conf import settings
from .models import Notification, NotificationRecipient


class NotificationRecipientSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    recipient_email = serializers.CharField(source='recipient.email', read_only=True)

    class Meta:
        model = NotificationRecipient
        fields = [
            'id', 'notification', 'recipient', 'recipient_name',
            'recipient_email', 'is_read', 'read_at', 'created_at',
        ]
        read_only_fields = ['id', 'is_read', 'read_at', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    sent_by_name = serializers.CharField(source='sent_by.get_full_name', read_only=True)
    recipients_count = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'attachment', 'sent_by', 'sent_by_name',
            'recipient_type', 'recipients_count', 'created_at',
        ]
        read_only_fields = ['id', 'sent_by', 'created_at']

    def get_recipients_count(self, obj):
        return obj.recipients.count()


class NotificationDetailSerializer(serializers.ModelSerializer):
    sent_by_name = serializers.CharField(source='sent_by.get_full_name', read_only=True)
    recipients = NotificationRecipientSerializer(many=True, read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'attachment', 'sent_by', 'sent_by_name',
            'recipient_type', 'recipients', 'created_at',
        ]


class NotificationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    attachment = serializers.FileField(required=False, allow_null=True)
    recipient_type = serializers.ChoiceField(
        choices=Notification.RECIPIENT_TYPE_CHOICES,
    )
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
    )
    recipient_pin_code = serializers.CharField(required=False, allow_blank=True)
    recipient_territory = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        recipient_type = attrs['recipient_type']

        if recipient_type == 'selected':
            if not attrs.get('recipient_ids'):
                raise serializers.ValidationError(
                    'recipient_ids is required when recipient_type is "selected".',
                )

        if recipient_type == 'pin_code':
            if not attrs.get('recipient_pin_code'):
                raise serializers.ValidationError(
                    'recipient_pin_code is required when recipient_type is "pin_code".',
                )

        if recipient_type == 'territory':
            if not attrs.get('recipient_territory'):
                raise serializers.ValidationError(
                    'recipient_territory is required when recipient_type is "territory".',
                )

        return attrs


class SendNotificationSerializer(serializers.ModelSerializer):
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
    )
    recipient_pin_code = serializers.CharField(required=False, allow_blank=True)
    recipient_territory = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'attachment', 'recipient_type',
            'recipient_ids', 'recipient_pin_code', 'recipient_territory',
        ]

    def validate(self, attrs):
        recipient_type = attrs.get('recipient_type')

        if recipient_type == 'selected' and not attrs.get('recipient_ids'):
            raise serializers.ValidationError(
                'recipient_ids is required when recipient_type is "selected".',
            )

        if recipient_type == 'pin_code' and not attrs.get('recipient_pin_code'):
            raise serializers.ValidationError(
                'recipient_pin_code is required when recipient_type is "pin_code".',
            )

        if recipient_type == 'territory' and not attrs.get('recipient_territory'):
            raise serializers.ValidationError(
                'recipient_territory is required when recipient_type is "territory".',
            )

        return attrs
