from django.contrib import admin
from .models import Reminder, FollowUp, PendingWork, Application


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'reminder_no', 'customer', 'service', 'reminder_type',
        'subject', 'due_date', 'priority', 'follow_up_status', 'created_at',
    ]
    list_filter = ['priority', 'follow_up_status', 'reminder_type']
    search_fields = ['reminder_no', 'subject', 'customer__head_of_family']
    readonly_fields = ['reminder_no', 'created_at', 'updated_at']


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'reminder', 'contact_date', 'next_follow_up',
        'contacted_by', 'created_at',
    ]
    list_filter = ['created_at']
    search_fields = ['reminder__reminder_no', 'customer_response']
    readonly_fields = ['created_at']


@admin.register(PendingWork)
class PendingWorkAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'pending_no', 'customer', 'service', 'pending_since',
        'expected_date', 'priority', 'work_status', 'created_at',
    ]
    list_filter = ['priority', 'work_status']
    search_fields = ['pending_no', 'customer__head_of_family', 'pending_reason']
    readonly_fields = ['pending_no', 'created_at', 'updated_at']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'application_no', 'applicant_name', 'applicant_mobile',
        'service', 'status', 'priority', 'payment_status',
        'total_fee', 'sla_days', 'created_at',
    ]
    list_filter = ['status', 'priority', 'payment_status']
    search_fields = ['application_no', 'applicant_name', 'applicant_mobile']
    readonly_fields = ['application_no', 'created_at', 'updated_at']
