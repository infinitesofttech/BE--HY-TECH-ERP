from django.db import models
from django.conf import settings


class EmailTemplate(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EmailCampaign(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('sent', 'Sent'), ('archived', 'Archived')]
    RECIPIENT_CHOICES = [('all', 'All Users'), ('selected', 'Selected Users'), ('pin_code', 'By Pin Code'), ('territory', 'By Territory')]
    CAMPAIGN_TYPE_CHOICES = [('regular', 'Regular'), ('automated', 'Automated'), ('triggered', 'Triggered')]
    PERIOD_CHOICES = [('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')]

    name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES, default='regular')
    subject = models.CharField(max_length=500)
    body = models.TextField()
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='all')
    recipient_ids = models.JSONField(default=list, blank=True)
    recipient_pin_code = models.CharField(max_length=10, blank=True)
    recipient_territory = models.CharField(max_length=100, blank=True)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    attachment = models.FileField(upload_to='campaign_attachments/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    sent_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
