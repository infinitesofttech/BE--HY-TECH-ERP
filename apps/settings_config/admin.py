from django.contrib import admin

from .models import (
    Department, Designation, CustomField, PrefixSetting,
    PrinterSetting, GDPRConsent, LocalizationSetting,
    LanguageSetting, AppearanceSetting, InvoiceSetting, SecuritySetting,
    Country, SmsGateway, EmailSetting, StorageSetting, SystemUpdate, NotificationSetting,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'department_head', 'description', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'department_head__email')


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'status', 'created_at')
    list_filter = ('status', 'department')
    search_fields = ('name', 'department__name')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'field_name', 'field_type', 'is_required', 'is_active')
    list_filter = ('model_name', 'field_type', 'is_active')
    search_fields = ('model_name', 'field_name')


@admin.register(PrefixSetting)
class PrefixSettingAdmin(admin.ModelAdmin):
    list_display = ('module', 'prefix', 'next_number', 'separator', 'example')
    list_filter = ('module',)


@admin.register(PrinterSetting)
class PrinterSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'printer_type', 'is_default', 'is_active')
    list_filter = ('printer_type', 'is_default', 'is_active')


@admin.register(GDPRConsent)
class GDPRConsentAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_type', 'is_accepted', 'accepted_at')
    list_filter = ('consent_type', 'is_accepted')


@admin.register(LocalizationSetting)
class LocalizationSettingAdmin(admin.ModelAdmin):
    list_display = ('timezone', 'date_format', 'time_format', 'currency_symbol')


@admin.register(LanguageSetting)
class LanguageSettingAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_default', 'is_active')
    list_filter = ('is_default', 'is_active')


@admin.register(AppearanceSetting)
class AppearanceSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'primary_color', 'sidebar_collapsed', 'font_size')


@admin.register(InvoiceSetting)
class InvoiceSettingAdmin(admin.ModelAdmin):
    list_display = ('prefix', 'next_number', 'show_tax', 'show_discount')


@admin.register(SecuritySetting)
class SecuritySettingAdmin(admin.ModelAdmin):
    list_display = ('password_min_length', 'require_special_char', 'require_number', 'max_login_attempts', 'session_timeout_minutes', 'two_factor_required')


@admin.register(SmsGateway)
class SmsGatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'sender_id', 'is_default', 'is_active')
    list_filter = ('is_default', 'is_active')
    search_fields = ('name',)


@admin.register(EmailSetting)
class EmailSettingAdmin(admin.ModelAdmin):
    list_display = ('mail_driver', 'host', 'port', 'encryption', 'from_email', 'from_name')


@admin.register(StorageSetting)
class StorageSettingAdmin(admin.ModelAdmin):
    list_display = ('driver', 'bucket', 'region', 'base_url')


@admin.register(SystemUpdate)
class SystemUpdateAdmin(admin.ModelAdmin):
    list_display = ('version', 'is_updated', 'last_checked_at')


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ('module', 'email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled')
