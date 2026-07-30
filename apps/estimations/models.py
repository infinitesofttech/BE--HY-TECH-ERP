from django.db import models
from django.conf import settings


class Estimation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('sent', 'Sent'), ('accepted', 'Accepted'),
        ('rejected', 'Rejected'), ('expired', 'Expired'),
    ]

    estimation_number = models.CharField(max_length=50, unique=True, blank=True)
    title = models.CharField(max_length=255, default='Estimation')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.estimation_number:
            last = Estimation.objects.all().aggregate(m=models.Max('id'))['m']
            self.estimation_number = f'EST-{(last or 0) + 1:05d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.estimation_number


class EstimationItem(models.Model):
    estimation = models.ForeignKey(
        Estimation, on_delete=models.CASCADE, related_name='items'
    )
    description = models.CharField(max_length=500)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.description} x {self.quantity}'


class Proposal(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('sent', 'Sent'), ('under_review', 'Under Review'),
        ('accepted', 'Accepted'), ('rejected', 'Rejected'),
    ]

    proposal_number = models.CharField(max_length=50, unique=True, blank=True)
    title = models.CharField(max_length=255, default='Proposal')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    content = models.TextField()
    version = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    valid_until = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.proposal_number:
            last = Proposal.objects.all().aggregate(m=models.Max('id'))['m']
            self.proposal_number = f'PRO-{(last or 0) + 1:05d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.proposal_number
