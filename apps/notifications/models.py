from django.db import models
from django.conf import settings


class Notification(models.Model):
    RECIPIENT_TYPE_CHOICES = [
        ('all', 'All'),
        ('selected', 'Selected'),
        ('pin_code', 'Pin Code'),
        ('territory', 'Territory'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    attachment = models.FileField(
        upload_to='notifications/', null=True, blank=True,
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
    )
    recipient_type = models.CharField(
        max_length=20,
        choices=RECIPIENT_TYPE_CHOICES,
        default='all',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class NotificationRecipient(models.Model):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='recipients',
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_notifications',
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['notification', 'recipient']
