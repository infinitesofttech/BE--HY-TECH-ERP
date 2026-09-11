from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class EmployeeUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'email', 'role',
            'phone', 'is_active', 'date_of_birth'
        ]
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_role(self, obj):
        if obj.is_superuser or obj.role in ['admin', 'hr']:
            return 'ADMIN'
        return 'STAFF'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'type', 'is_read', 'link', 'created_at']
        read_only_fields = ['id', 'created_at']



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'type', 'is_read', 'link', 'created_at']
        read_only_fields = ['id', 'created_at']
