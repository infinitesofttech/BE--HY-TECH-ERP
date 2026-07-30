from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=200)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Cities'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.state.name if self.state else "N/A"}'


class CustomField(models.Model):
    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('select', 'Select'),
        ('boolean', 'Boolean'),
    ]
    model_name = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)
    options = models.JSONField(blank=True, default=list, help_text='Options for select type fields')
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['model_name', 'field_name']

    def __str__(self):
        return f'{self.model_name} - {self.field_name}'


class PrefixSetting(models.Model):
    MODULE_CHOICES = [
        ('invoice', 'Invoice'),
        ('estimation', 'Estimation'),
        ('proposal', 'Proposal'),
        ('ticket', 'Ticket'),
    ]
    module = models.CharField(max_length=50, choices=MODULE_CHOICES, unique=True)
    prefix = models.CharField(max_length=20, default='')
    next_number = models.PositiveIntegerField(default=1)
    separator = models.CharField(max_length=10, default='-')
    example = models.CharField(max_length=100, blank=True, editable=False)

    class Meta:
        ordering = ['module']

    def save(self, *args, **kwargs):
        self.example = f'{self.prefix}{self.separator}{self.next_number}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.module}: {self.example}'


class PrinterSetting(models.Model):
    PRINTER_TYPE_CHOICES = [
        ('thermal', 'Thermal'),
        ('a4', 'A4'),
        ('pos', 'POS'),
    ]
    name = models.CharField(max_length=200)
    printer_type = models.CharField(max_length=20, choices=PRINTER_TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GDPRConsent(models.Model):
    CONSENT_TYPE_CHOICES = [
        ('privacy_policy', 'Privacy Policy'),
        ('terms_conditions', 'Terms & Conditions'),
        ('marketing', 'Marketing'),
        ('data_processing', 'Data Processing'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gdpr_consents')
    consent_type = models.CharField(max_length=50, choices=CONSENT_TYPE_CHOICES)
    is_accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'consent_type']
        ordering = ['-accepted_at']

    def __str__(self):
        return f'{self.user} - {self.consent_type}: {self.is_accepted}'


class LocalizationSetting(models.Model):
    timezone = models.CharField(max_length=100, default='UTC')
    date_format = models.CharField(max_length=50, default='YYYY-MM-DD')
    time_format = models.CharField(max_length=50, default='HH:mm:ss')
    currency_symbol = models.CharField(max_length=10, default='$')
    decimal_separator = models.CharField(max_length=5, default='.')
    thousand_separator = models.CharField(max_length=5, default=',')

    class Meta:
        verbose_name = 'Localization Setting'

    def __str__(self):
        return f'Localization: {self.timezone}'


class LanguageSetting(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class AppearanceSetting(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='appearance_settings')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    primary_color = models.CharField(max_length=20, default='#1976D2')
    sidebar_collapsed = models.BooleanField(default=False)
    font_size = models.CharField(max_length=10, default='medium')

    class Meta:
        verbose_name = 'Appearance Setting'

    def __str__(self):
        return f'Appearance: {self.theme}'


class InvoiceSetting(models.Model):
    prefix = models.CharField(max_length=20, default='INV')
    next_number = models.PositiveIntegerField(default=1)
    default_terms = models.TextField(blank=True, default='')
    default_payment_method = models.CharField(max_length=100, blank=True, default='')
    show_tax = models.BooleanField(default=True)
    show_discount = models.BooleanField(default=True)
    footer_text = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Invoice Setting'

    def __str__(self):
        return f'Invoice Settings (next: {self.prefix}-{self.next_number})'


class SecuritySetting(models.Model):
    password_min_length = models.PositiveIntegerField(default=8)
    require_special_char = models.BooleanField(default=True)
    require_number = models.BooleanField(default=True)
    max_login_attempts = models.PositiveIntegerField(default=5)
    session_timeout_minutes = models.PositiveIntegerField(default=60)
    two_factor_required = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Security Setting'

    def __str__(self):
        return 'Security Settings'
