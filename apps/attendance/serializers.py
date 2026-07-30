from rest_framework import serializers
from .models import AttendanceType, Attendance


class AttendanceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceType
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    employee_email = serializers.CharField(source='employee.email', read_only=True)
    attendance_type_name = serializers.CharField(source='attendance_type.name', read_only=True, default='')

    class Meta:
        model = Attendance
        fields = '__all__'


class AttendancePunchInSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    address = serializers.CharField(max_length=500, required=False, allow_blank=True)


class AttendancePunchOutSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    address = serializers.CharField(max_length=500, required=False, allow_blank=True)
