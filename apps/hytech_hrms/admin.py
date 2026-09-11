from django.contrib import admin
from .models import (
    AttendanceRecord, LeaveRecord, LeaveBalance, HolidayItem,
    HRCompanySetting, HRAttendanceSetting, HRLeaveSetting,
    HRNotificationSetting, HRRolePermission
)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'employee', 'date', 'day_name', 'in_time',
        'out_time', 'status', 'work_hours',
    ]
    list_filter = ['status', 'date']
    search_fields = ['employee__email', 'employee__first_name', 'employee__last_name']


@admin.register(LeaveRecord)
class LeaveRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'employee', 'leave_type', 'start_date',
        'end_date', 'days_count', 'status', 'applied_at',
    ]
    list_filter = ['leave_type', 'status', 'applied_at']
    search_fields = ['employee__email', 'reason']
    readonly_fields = ['applied_at']


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'employee',
        'casual_total', 'casual_used',
        'sick_total', 'sick_used',
        'paid_total', 'paid_used',
    ]
    search_fields = ['employee__email', 'employee__first_name', 'employee__last_name']


@admin.register(HolidayItem)
class HolidayItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date', 'day', 'type']
    list_filter = ['type', 'date']
    search_fields = ['title', 'title_gu']


@admin.register(HRCompanySetting)
class HRCompanySettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'organization_name', 'opening_time', 'closing_time', 'contact_phone', 'updated_at']


@admin.register(HRAttendanceSetting)
class HRAttendanceSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'shift_start_time', 'shift_end_time', 'grace_period_label', 'half_day_cutoff_time', 'updated_at']


@admin.register(HRLeaveSetting)
class HRLeaveSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'annual_casual_leave', 'annual_sick_leave', 'annual_paid_leave', 'updated_at']


@admin.register(HRNotificationSetting)
class HRNotificationSettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'whatsapp_daily_punch_summary', 'sms_leave_approval', 'email_leave_notifications', 'updated_at']


@admin.register(HRRolePermission)
class HRRolePermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'display_name', 'can_manage_employees', 'can_approve_leaves', 'can_manage_payroll', 'can_manage_settings']
    list_filter = ['role']

