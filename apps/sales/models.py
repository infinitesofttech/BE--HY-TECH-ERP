from django.db import models
from django.conf import settings


class SalesReport(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sales_reports',
    )
    dealer = models.ForeignKey(
        'masters.Dealer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sales_reports',
    )
    date = models.DateField()
    total_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    total_items = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f'{self.employee} - {self.date}'


class SalesReportItem(models.Model):
    report = models.ForeignKey(
        SalesReport,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.product} x{self.quantity}'

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
