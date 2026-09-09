from django.db import models, transaction
from django.conf import settings


class Ticket(models.Model):
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')]
    STATUS_CHOICES = [('open', 'Open'), ('in_progress', 'In Progress'), ('resolved', 'Resolved'), ('closed', 'Closed')]

    ticket_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    category = models.CharField(max_length=100, blank=True)
    due_date = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to='ticket_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ticket_id} - {self.subject}'

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            with transaction.atomic():
                last = Ticket.objects.select_for_update().order_by('-id').first()
                self.ticket_id = f'TKT-{(last.id if last else 0) + 1:04d}'
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='ticket_replies/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Reply to {self.ticket.ticket_id} by {self.user.email}'
