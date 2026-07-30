import uuid

from django.conf import settings
from django.db import models


class Invitation(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('msr', 'MSR'),
        ('dealer', 'Dealer'),
        ('retailer', 'Retailer'),
        ('mechanic', 'Mechanic'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invitations_sent',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Invitation for {self.email} ({self.status})'
