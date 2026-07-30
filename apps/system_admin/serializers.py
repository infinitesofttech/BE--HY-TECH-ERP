from rest_framework import serializers
from .models import BackupLog, CronJob, BannedIP, ConnectedApp


class BackupLogSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, default='')

    class Meta:
        model = BackupLog
        fields = '__all__'
        read_only_fields = ['id', 'started_at', 'created_by']


class BackupLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupLog
        fields = ['filename', 'file_size', 'backup_type', 'notes']


class CronJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronJob
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'last_run_at', 'last_status']


class CronJobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronJob
        fields = ['name', 'command', 'schedule', 'is_active']


class BannedIPSerializer(serializers.ModelSerializer):
    banned_by_name = serializers.CharField(source='banned_by.get_full_name', read_only=True, default='')

    class Meta:
        model = BannedIP
        fields = '__all__'
        read_only_fields = ['id', 'banned_at', 'banned_by']


class BannedIPCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannedIP
        fields = ['ip_address', 'reason', 'expires_at']


class ConnectedAppSerializer(serializers.ModelSerializer):
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = ConnectedApp
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def get_client_secret(self, obj):
        if obj.client_secret:
            return obj.client_secret[:6] + '*' * (len(obj.client_secret) - 6)
        return ''


class ConnectedAppCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedApp
        fields = ['name', 'app_type', 'client_id', 'client_secret', 'is_active']
