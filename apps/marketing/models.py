from django.db import models
from django.conf import settings


class Campaign(models.Model):
    CAMPAIGN_TYPE_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('social', 'Social'),
        ('email', 'Email'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=500, blank=True, default='')
    title = models.CharField(max_length=500, blank=True, default='')
    message = models.TextField(blank=True, default='')
    content = models.TextField(blank=True, default='')
    recipient_filter = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    stats_sent_count = models.IntegerField(default=0)
    stats_opened_count = models.IntegerField(default=0)
    stats_clicked_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CampaignAttachment(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='campaign_attachments/')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
