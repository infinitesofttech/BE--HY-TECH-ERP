from rest_framework import serializers
from django.utils import timezone
from .models import Reminder, FollowUp, PendingWork, Application


class FollowUpSerializer(serializers.ModelSerializer):
    contacted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = FollowUp
        fields = [
            'id', 'reminder', 'contact_date', 'customer_response',
            'next_follow_up', 'notes', 'contacted_by', 'contacted_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_contacted_by_name(self, obj):
        if obj.contacted_by:
            return obj.contacted_by.get_full_name() or obj.contacted_by.username
        return "Staff Member"

    def create(self, validated_data):
        follow_up = super().create(validated_data)
        reminder = follow_up.reminder
        if reminder:
            reminder.customer_response = follow_up.customer_response
            reminder.next_follow_up = follow_up.next_follow_up
            reminder.last_contact_date = timezone.now()
            reminder.save(update_fields=['customer_response', 'next_follow_up', 'last_contact_date'])
        return follow_up


class ReminderSerializer(serializers.ModelSerializer):
    customer_family_id = serializers.CharField(source='customer.family_id', read_only=True)
    customer_name = serializers.CharField(source='customer.head_of_family', read_only=True)
    customer_mobile = serializers.CharField(source='customer.mobile_number', read_only=True)
    service_name = serializers.CharField(source='service.ServiceName', read_only=True, default='')
    follow_ups = FollowUpSerializer(many=True, read_only=True)
    follow_up_count = serializers.SerializerMethodField()

    class Meta:
        model = Reminder
        fields = [
            'id', 'reminder_no', 'customer', 'customer_family_id',
            'customer_name', 'customer_mobile', 'service', 'service_name',
            'reminder_type', 'subject', 'due_date', 'reminder_date',
            'priority', 'message_template', 'follow_up_status', 'notes',
            'last_contact_date', 'customer_response', 'next_follow_up',
            'follow_ups', 'follow_up_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reminder_no', 'created_at', 'updated_at']

    def get_follow_up_count(self, obj):
        return obj.follow_ups.count()


class PendingWorkSerializer(serializers.ModelSerializer):
    customer_family_id = serializers.CharField(source='customer.family_id', read_only=True)
    customer_name = serializers.CharField(source='customer.head_of_family', read_only=True)
    customer_mobile = serializers.CharField(source='customer.mobile_number', read_only=True)
    service_name = serializers.CharField(source='service.ServiceName', read_only=True, default='')
    assigned_staff_name = serializers.SerializerMethodField()

    class Meta:
        model = PendingWork
        fields = [
            'id', 'pending_no', 'service_visit', 'customer', 'customer_family_id',
            'customer_name', 'customer_mobile', 'service', 'service_name',
            'pending_since', 'expected_date', 'priority', 'pending_reason',
            'documents_pending', 'assigned_staff', 'assigned_staff_name',
            'next_action', 'work_status', 'follow_up_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'pending_no', 'created_at', 'updated_at']

    def get_assigned_staff_name(self, obj):
        if obj.assigned_staff:
            return obj.assigned_staff.get_full_name() or obj.assigned_staff.username
        return "Staff Officer"


class ApplicationSerializer(serializers.ModelSerializer):
    customer_family_id = serializers.CharField(source='customer.family_id', read_only=True, default='')
    customer_name = serializers.SerializerMethodField()
    customer_mobile = serializers.SerializerMethodField()
    family_member_name = serializers.CharField(source='family_member.name', read_only=True, default='')
    service_name = serializers.CharField(source='service.ServiceName', read_only=True, default='')
    service_name_gu = serializers.CharField(source='service.ServiceNameGu', read_only=True, default='')
    sub_service_name = serializers.CharField(source='sub_service.SubServiceName', read_only=True, default='')
    assigned_staff_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'application_no', 'customer', 'customer_name', 'customer_mobile',
            'customer_family_id', 'applicant_name', 'applicant_mobile',
            'family_member', 'family_member_name', 'service', 'service_name',
            'service_name_gu', 'sub_service', 'sub_service_name', 'category',
            'status', 'priority', 'government_app_no', 'government_portal_url',
            'govt_fee', 'service_charge', 'total_fee', 'payment_status',
            'payment_mode', 'receipt_no', 'assigned_staff', 'assigned_staff_name',
            'created_by', 'created_by_name', 'expected_date', 'sla_days',
            'documents', 'form_data', 'timeline', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'application_no', 'created_at', 'updated_at']

    def get_customer_name(self, obj):
        if obj.applicant_name:
            return obj.applicant_name
        if obj.customer:
            return obj.customer.head_of_family
        return ""

    def get_customer_mobile(self, obj):
        if obj.applicant_mobile:
            return obj.applicant_mobile
        if obj.customer:
            return obj.customer.mobile_number
        return ""

    def get_assigned_staff_name(self, obj):
        if obj.assigned_staff:
            return obj.assigned_staff.get_full_name() or obj.assigned_staff.username
        return "Staff Officer"

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return "Admin"
