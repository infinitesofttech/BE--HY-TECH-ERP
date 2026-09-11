from rest_framework import serializers
from .models import (
    AttendanceRecord, LeaveRecord, LeaveBalance, HolidayItem,
    HRCompanySetting, HRAttendanceSetting, HRLeaveSetting,
    HRNotificationSetting, HRRolePermission
)


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


class HRCompanySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRCompanySetting
        fields = [
            'id', 'organization_name', 'opening_time', 'closing_time',
            'contact_email', 'contact_phone', 'address', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class HRAttendanceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRAttendanceSetting
        fields = [
            'id', 'grace_period_minutes', 'grace_period_label',
            'half_day_cutoff_time', 'shift_start_time', 'shift_end_time',
            'standard_work_hours', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class HRLeaveSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRLeaveSetting
        fields = [
            'id', 'annual_casual_leave', 'annual_sick_leave',
            'annual_paid_leave', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class HRNotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRNotificationSetting
        fields = [
            'id', 'whatsapp_daily_punch_summary', 'sms_leave_approval',
            'email_leave_notifications', 'admin_whatsapp_number', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class HRRolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRRolePermission
        fields = [
            'id', 'role', 'display_name', 'description',
            'can_manage_employees', 'can_view_attendance', 'can_mark_attendance',
            'can_approve_leaves', 'can_manage_payroll', 'can_view_reports',
            'can_manage_settings', 'can_process_services', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class HRAllSettingsSerializer(serializers.Serializer):
    company = HRCompanySettingSerializer()
    attendance = HRAttendanceSettingSerializer()
    leave = HRLeaveSettingSerializer()
    notifications = HRNotificationSettingSerializer()
    roles = HRRolePermissionSerializer(many=True)

