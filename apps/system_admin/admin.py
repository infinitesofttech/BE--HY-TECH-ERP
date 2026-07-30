from django.contrib import admin
from .models import BackupLog, CronJob, BannedIP, ConnectedApp


@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ['filename', 'backup_type', 'status', 'started_at', 'completed_at']
    list_filter = ['backup_type', 'status']
    search_fields = ['filename', 'notes']


@admin.register(CronJob)
class CronJobAdmin(admin.ModelAdmin):
    list_display = ['name', 'schedule', 'is_active', 'last_run_at', 'last_status']
    list_filter = ['is_active', 'last_status']
    search_fields = ['name']


@admin.register(BannedIP)
class BannedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'banned_at', 'expires_at']
    search_fields = ['ip_address', 'reason']


@admin.register(ConnectedApp)
class ConnectedAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'app_type', 'is_active', 'created_at']
    list_filter = ['app_type', 'is_active']
    search_fields = ['name']
