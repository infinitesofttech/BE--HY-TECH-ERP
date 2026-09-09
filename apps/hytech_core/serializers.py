from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class EmployeeUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'email', 'role',
            'phone', 'is_active', 'designation', 'department',
            'joining_date', 'salary', 'date_of_birth'
        ]
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_role(self, obj):
        if obj.is_superuser or obj.role in ['super_admin', 'manager', 'admin']:
            return 'ADMIN'
        return 'STAFF'

    def get_designation(self, obj):
        if obj.designation:
            return obj.designation.name
        return "Center Operator"

    def get_department(self, obj):
        if obj.department:
            return obj.department.name
        return "Operations"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'type', 'is_read', 'link', 'created_at']
        read_only_fields = ['id', 'created_at']
