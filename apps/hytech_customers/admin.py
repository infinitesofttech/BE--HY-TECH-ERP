from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-id']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'date_of_birth')}),
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'family_id', 'head_of_family', 'mobile_number',
        'village_city', 'current_points', 'wallet_balance',
        'total_visits', 'is_active', 'created_at',
    ]
    list_filter = ['is_active', 'document_consent', 'digital_card_sent']
    search_fields = ['family_id', 'head_of_family', 'mobile_number', 'whatsapp_number']
    readonly_fields = ['family_id', 'created_at', 'updated_at']


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'customer', 'relationship', 'gender',
        'mobile_number', 'birth_date', 'is_active',
    ]
    list_filter = ['relationship', 'gender', 'is_active']
    search_fields = ['name', 'mobile_number', 'family_id']


@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'document_name', 'document_type', 'customer',
        'member_name', 'is_verified', 'created_at',
    ]
    list_filter = ['document_type', 'is_verified']
    search_fields = ['document_name', 'family_id', 'member_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ServiceVisit)
class ServiceVisitAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'visit_no', 'customer', 'service', 'status',
        'visit_date', 'created_at',
    ]
    list_filter = ['status', 'visit_date']
    search_fields = ['visit_no', 'customer__head_of_family', 'customer__family_id']
    readonly_fields = ['visit_no', 'created_at', 'updated_at']


@admin.register(VisitDocument)
class VisitDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'document_name', 'document_type', 'visit',
        'status', 'created_at',
    ]
    list_filter = ['status', 'document_type']
    search_fields = ['document_name']
    readonly_fields = ['created_at', 'updated_at']
