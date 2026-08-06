from rest_framework import serializers
from .models import (
    Department, Designation, CustomField, PrefixSetting,
    PrinterSetting, GDPRConsent, LocalizationSetting,
    LanguageSetting, AppearanceSetting, InvoiceSetting, SecuritySetting,
    Country, SmsGateway, EmailSetting, StorageSetting, SystemUpdate, NotificationSetting,
)


class DepartmentSerializer(serializers.ModelSerializer):
    department_head_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'department_head', 'department_head_name',
            'description', 'status', 'employee_count', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_department_head_name(self, obj):
        if obj.department_head:
            return obj.department_head.get_full_name() or obj.department_head.email
        return None

    def get_employee_count(self, obj):
        count = getattr(obj, 'employee_count', None)
        return count if count is not None else obj.employees.count()


class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'department_head', 'description', 'status']


class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True, default='')
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Designation
        fields = [
            'id', 'name', 'department', 'department_name', 'status',
            'employee_count', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_employee_count(self, obj):
        count = getattr(obj, 'employee_count', None)
        return count if count is not None else obj.employees.count()


class DesignationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'name', 'department', 'status']


class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class CustomFieldCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = ['model_name', 'field_name', 'field_type', 'options', 'is_required', 'is_active']


class PrefixSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrefixSetting
        fields = '__all__'
        read_only_fields = ['id', 'example']

    def validate(self, attrs):
        prefix = attrs.get('prefix', '')
        next_number = attrs.get('next_number', 1)
        separator = attrs.get('separator', '-')
        attrs['example'] = f'{prefix}{separator}{next_number}'
        return attrs


class PrinterSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrinterSetting
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class GDPRConsentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True, default='')

    class Meta:
        model = GDPRConsent
        fields = '__all__'
        read_only_fields = ['id', 'accepted_at']


class LocalizationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalizationSetting
        fields = '__all__'
        read_only_fields = ['id']


class LanguageSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageSetting
        fields = '__all__'
        read_only_fields = ['id']


class AppearanceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppearanceSetting
        fields = '__all__'
        read_only_fields = ['id', 'user']


class InvoiceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceSetting
        fields = '__all__'
        read_only_fields = ['id']


class SecuritySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecuritySetting
        fields = '__all__'
        read_only_fields = ['id']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class SmsGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsGateway
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class EmailSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSetting
        fields = '__all__'
        read_only_fields = ['id']


class StorageSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageSetting
        fields = '__all__'
        read_only_fields = ['id']


class SystemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemUpdate
        fields = '__all__'
        read_only_fields = ['id']


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = '__all__'
        read_only_fields = ['id', 'updated_at']
