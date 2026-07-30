from rest_framework import serializers
from django.utils import timezone
from .models import TrackingLocation


class TrackingLocationSerializer(serializers.ModelSerializer):
    employee_email = serializers.SerializerMethodField()

    class Meta:
        model = TrackingLocation
        fields = [
            'id', 'employee', 'employee_email', 'latitude', 'longitude',
            'speed', 'address', 'battery_level', 'timestamp', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_employee_email(self, obj):
        return obj.employee.email if obj.employee else None


class LocationUpdateSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    speed = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    battery_level = serializers.IntegerField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField(required=False, default=None)

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate_battery_level(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Battery level must be between 0 and 100.")
        return value


class LiveLocationSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    speed = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    last_updated = serializers.DateTimeField()
    battery_level = serializers.IntegerField(allow_null=True)
