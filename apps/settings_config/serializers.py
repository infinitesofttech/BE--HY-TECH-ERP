from rest_framework import serializers
from .models import (
    Department, State, City, CustomField, PrefixSetting,
    PrinterSetting, GDPRConsent, LocalizationSetting,
    LanguageSetting, AppearanceSetting, InvoiceSetting, SecuritySetting,
)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'description', 'is_active']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True, default='')

    class Meta:
        model = City
        fields = '__all__'
        read_only_fields = ['id']


class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'state', 'is_active']


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
