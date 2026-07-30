from django.db import models
from django.conf import settings


class BackupLog(models.Model):
    BACKUP_TYPE_CHOICES = [
        ('database', 'Database'),
        ('files', 'Files'),
        ('full', 'Full'),
    ]
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    filename = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backup_logs',
    )

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.filename} ({self.backup_type}) - {self.status}'


class CronJob(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    name = models.CharField(max_length=200, unique=True)
    command = models.TextField()
    schedule = models.CharField(max_length=200, help_text='Cron expression (e.g., "0 */6 * * *")')
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BannedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.TextField(blank=True, default='')
    banned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='banned_ips',
    )
    banned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-banned_at']

    def __str__(self):
        return self.ip_address


class ConnectedApp(models.Model):
    APP_TYPE_CHOICES = [
        ('oauth2', 'OAuth2'),
        ('api_key', 'API Key'),
        ('webhook', 'Webhook'),
    ]

    name = models.CharField(max_length=200, unique=True)
    app_type = models.CharField(max_length=20, choices=APP_TYPE_CHOICES)
    client_id = models.CharField(max_length=500)
    client_secret = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
