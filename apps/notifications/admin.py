from django.contrib import admin
from .models import Notification, NotificationRecipient


class NotificationRecipientInline(admin.TabularInline):
    model = NotificationRecipient
    extra = 0
    readonly_fields = ['recipient', 'is_read', 'read_at', 'created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'sent_by', 'recipient_type',
        'recipients_count', 'created_at',
    ]
    list_filter = ['recipient_type', 'created_at']
    search_fields = ['title', 'message', 'sent_by__email']
    inlines = [NotificationRecipientInline]

    def recipients_count(self, obj):
        return obj.recipients.count()
    recipients_count.short_description = 'Recipients'


@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'notification', 'recipient', 'is_read', 'read_at', 'created_at',
    ]
    list_filter = ['is_read', 'created_at']
    search_fields = [
        'recipient__email', 'recipient__first_name', 'recipient__last_name',
        'notification__title',
    ]
