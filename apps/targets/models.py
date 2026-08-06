from django.db import models
from django.conf import settings


class Team(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=200)
    team_lead = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='led_teams',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='teams',
    )
    target_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Target(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'), ('achieved', 'Achieved'),
        ('missed', 'Missed'), ('inactive', 'Inactive'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='targets',
    )
    team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='targets',
    )
    month = models.IntegerField()
    year = models.IntegerField()
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    achieved_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    product = models.ForeignKey(
        'products.Product',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='targets',
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['employee', 'month', 'year', 'product']

    def __str__(self):
        product_name = self.product.name if self.product else 'All Products'
        return f'{self.employee} - {self.month}/{self.year} - {product_name}'
