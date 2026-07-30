import uuid
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    invited_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = [
            'id', 'token', 'invited_by', 'sent_at',
            'accepted_at', 'expires_at', 'created_at',
        ]

    def get_invited_by_name(self, obj):
        return obj.invited_by.email if obj.invited_by else None


class InvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['email', 'role']

    def create(self, validated_data):
        validated_data['token'] = uuid.uuid4()
        validated_data['expires_at'] = timezone.now() + timedelta(days=7)
        return super().create(validated_data)
