from django.contrib import admin
from .models import LeaveType, Leave, LeaveApprovalWorkflow, LeaveAllocation


@admin.register(LeaveAllocation)
class LeaveAllocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'leave_type', 'allotted_days', 'updated_at']
    list_filter = ['leave_type']
    search_fields = ['employee__email', 'employee__first_name']


@admin.register(LeaveApprovalWorkflow)
class LeaveApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'approver', 'priority', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['employee__email', 'approver__email', 'employee__first_name', 'approver__first_name']


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'days_allowed', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'employee', 'leave_type', 'start_date', 'end_date',
        'total_days', 'status', 'assigned_approver', 'approved_by', 'created_at',
    ]
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = [
        'employee__email', 'employee__first_name', 'employee__last_name',
    ]
    readonly_fields = ['total_days', 'approved_by', 'approved_at']
