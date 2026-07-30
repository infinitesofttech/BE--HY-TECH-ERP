from django.db import models
from django.conf import settings


class AttendanceType(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Attendance Types'

    def __str__(self):
        return self.name


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('late', 'Late'),
    ]
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances'
    )
    date = models.DateField()
    attendance_type = models.ForeignKey(
        AttendanceType, on_delete=models.SET_NULL, null=True, blank=True
    )
    punch_in_time = models.DateTimeField(null=True, blank=True)
    punch_in_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    punch_in_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    punch_in_address = models.CharField(max_length=500, blank=True)
    punch_out_time = models.DateTimeField(null=True, blank=True)
    punch_out_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    punch_out_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    punch_out_address = models.CharField(max_length=500, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"

    def save(self, *args, **kwargs):
        if self.punch_in_time and self.punch_out_time:
            diff = self.punch_out_time - self.punch_in_time
            hours = diff.total_seconds() / 3600
            self.total_hours = round(hours, 2)
            if hours > 8:
                self.overtime = round(hours - 8, 2)
        super().save(*args, **kwargs)
