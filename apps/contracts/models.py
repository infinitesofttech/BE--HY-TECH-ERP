from django.db import models
from django.conf import settings


class Contract(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'), ('expired', 'Expired'),
        ('terminated', 'Terminated'), ('draft', 'Draft'),
    ]

    title = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    contract_type = models.CharField(max_length=100, blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft'
    )
    description = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to='contracts/', blank=True, null=True
    )
    signature = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
