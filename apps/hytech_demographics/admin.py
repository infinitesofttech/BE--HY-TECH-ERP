from django.contrib import admin
from .models import Village, ContactInquiry, AuditLog


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'code', 'name', 'taluka', 'district',
        'total_families', 'total_citizens', 'male_count',
        'female_count', 'is_active',
    ]
    list_filter = ['district', 'taluka', 'is_active']
    search_fields = ['code', 'name', 'taluka', 'district']
    readonly_fields = ['code', 'created_at']


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'full_name', 'mobile_number', 'email',
        'subject', 'status', 'assigned_to', 'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'mobile_number', 'email', 'subject']
    readonly_fields = ['created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'timestamp', 'user_name', 'user_role',
        'action', 'entity_type', 'entity_id', 'ip_address',
    ]
    list_filter = ['action', 'entity_type', 'user_role']
    search_fields = ['user_name', 'entity_type', 'entity_id', 'details']
    readonly_fields = ['timestamp']
