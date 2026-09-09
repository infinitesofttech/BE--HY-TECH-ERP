from rest_framework import serializers
from .models import AttendanceRecord, LeaveRecord, LeaveBalance, HolidayItem


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_id = serializers.IntegerField(source='employee.id', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'employee', 'employee_id', 'date', 'day_name',
            'in_time', 'out_time', 'status', 'work_hours', 'notes'
        ]
        read_only_fields = ['id', 'day_name']

    def create(self, validated_data):
        date_val = validated_data.get('date')
        if date_val and not validated_data.get('day_name'):
            validated_data['day_name'] = date_val.strftime('%A')
        
        employee = validated_data.get('employee')
        rec, created = AttendanceRecord.objects.update_or_create(
            employee=employee,
            date=date_val,
            defaults=validated_data
        )
        return rec


class LeaveRecordSerializer(serializers.ModelSerializer):
    employee_id = serializers.IntegerField(source='employee.id', read_only=True)

    class Meta:
        model = LeaveRecord
        fields = [
            'id', 'employee', 'employee_id', 'leave_type', 'start_date',
            'end_date', 'days_count', 'reason', 'status', 'applied_at',
            'approved_by'
        ]
        read_only_fields = ['id', 'applied_at']


class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = [
            'casual_total', 'casual_used', 'sick_total', 'sick_used',
            'paid_total', 'paid_used'
        ]


class HolidayItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayItem
        fields = ['id', 'title', 'title_gu', 'date', 'day', 'type', 'description']
