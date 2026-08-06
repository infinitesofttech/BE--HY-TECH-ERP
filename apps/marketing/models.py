from django.db import models
from django.conf import settings


class Campaign(models.Model):
    CAMPAIGN_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('ending_soon', 'Ending Soon'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    TARGET_AUDIENCE_CHOICES = [
        ('customers', 'Customers'),
        ('leads', 'Leads'),
        ('subscribers', 'Subscribers'),
    ]
    PERIOD_CHOICES = [
        ('days', 'Days'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    CURRENCY_CHOICES = [
        ('usd', 'Dollar'),
        ('eur', 'Euro'),
        ('gbp', 'Pound'),
        ('inr', 'Rupee'),
    ]

    type = models.CharField(
        max_length=20, choices=CAMPAIGN_TYPE_CHOICES, default='basic',
    )
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=500, blank=True, default='')
    title = models.CharField(max_length=500, blank=True, default='')
    message = models.TextField(blank=True, default='')
    content = models.TextField(blank=True, default='')
    recipient_filter = models.JSONField(default=dict, blank=True)
    deal_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=20, choices=CURRENCY_CHOICES, blank=True, default='')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, blank=True, default='')
    period_value = models.CharField(max_length=100, blank=True, default='')
    target_audience = models.JSONField(
        default=list, blank=True,
        help_text='List of audience groups: customers, leads, subscribers.',
    )
    description = models.TextField(blank=True, default='')
    attachment = models.FileField(upload_to='campaign_attachments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
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
