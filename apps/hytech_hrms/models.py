from django.db import models
from django.conf import settings
from django.utils import timezone


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
        ('HOLIDAY', 'Holiday'),
        ('LEAVE', 'Leave'),
    ]

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hytech_attendances')
    date = models.DateField(default=timezone.now)
    day_name = models.CharField(max_length=50, blank=True)
    in_time = models.CharField(max_length=50, blank=True, null=True)
    out_time = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PRESENT')
    work_hours = models.FloatField(default=0.0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date', 'employee']
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.username} - {self.date} [{self.status}]"


class LeaveRecord(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('CASUAL', 'Casual Leave'),
        ('SICK', 'Sick Leave'),
        ('PAID', 'Paid Leave'),
        ('UNPAID', 'Unpaid Leave'),
    ]
    STATUS_CHOICES = [
        ('APPROVED', 'Approved'),
        ('PENDING', 'Pending'),
        ('REJECTED', 'Rejected'),
    ]

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hytech_leaves')
    leave_type = models.CharField(max_length=30, choices=LEAVE_TYPE_CHOICES, default='CASUAL')
    start_date = models.DateField()
    end_date = models.DateField()
    days_count = models.PositiveIntegerField(default=1)
    reason = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.days_count} days) [{self.status}]"


class LeaveBalance(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hytech_leave_balance')
    casual_total = models.IntegerField(default=12)
    casual_used = models.IntegerField(default=0)
    sick_total = models.IntegerField(default=7)
    sick_used = models.IntegerField(default=0)
    paid_total = models.IntegerField(default=5)
    paid_used = models.IntegerField(default=0)

    def __str__(self):
        return f"Leave Balance - {self.employee.username}"


class HolidayItem(models.Model):
    TYPE_CHOICES = [
        ('GOVERNMENT', 'Government Holiday'),
        ('REGIONAL', 'Regional Holiday'),
        ('NATIONAL', 'National Holiday'),
    ]

    title = models.CharField(max_length=200)
    title_gu = models.CharField(max_length=200)
    date = models.DateField()
    day = models.CharField(max_length=50)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='GOVERNMENT')
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} ({self.date})"
