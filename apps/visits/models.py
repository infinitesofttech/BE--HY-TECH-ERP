from django.db import models
from django.conf import settings


class Visit(models.Model):
    VISIT_TYPE_CHOICES = [
        ('dealer', 'Dealer'),
        ('retailer', 'Retailer'),
    ]
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visits',
    )
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES)
    dealer = models.ForeignKey(
        'masters.Dealer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
    )
    retailer = models.ForeignKey(
        'masters.Retailer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits',
    )
    purpose = models.CharField(max_length=200, blank=True)
    remarks = models.TextField(blank=True)
    photo = models.ImageField(upload_to='visits/', null=True, blank=True)

    check_in_time = models.DateTimeField(auto_now_add=True)
    check_in_lat = models.DecimalField(max_digits=9, decimal_places=6)
    check_in_lng = models.DecimalField(max_digits=9, decimal_places=6)
    check_in_address = models.CharField(max_length=500, blank=True)

    check_out_time = models.DateTimeField(null=True, blank=True)
    check_out_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
    )
    check_out_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
    )
    check_out_address = models.CharField(max_length=500, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_progress',
    )
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.employee} - {self.visit_type} - {self.check_in_time}"

    def save(self, *args, **kwargs):
        if self.check_in_time and self.check_out_time:
            self.duration = self.check_out_time - self.check_in_time
        super().save(*args, **kwargs)
