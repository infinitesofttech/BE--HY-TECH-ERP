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


class HRCompanySetting(models.Model):
    organization_name = models.CharField(max_length=255, default="HY-TECH CITIZEN SERVICES & COMPUTER HUB")
    opening_time = models.CharField(max_length=50, default="09:00 AM")
    closing_time = models.CharField(max_length=50, default="07:00 PM")
    contact_email = models.EmailField(max_length=100, blank=True, default="contact@hytech.com")
    contact_phone = models.CharField(max_length=50, blank=True, default="+91 98765 43210")
    address = models.TextField(blank=True, default="Opp. Bus Station, Main Road, Gujarat")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "HR Company Setting"
        verbose_name_plural = "HR Company Settings"

    def __str__(self):
        return self.organization_name

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class HRAttendanceSetting(models.Model):
    grace_period_minutes = models.IntegerField(default=15)
    grace_period_label = models.CharField(max_length=50, default="15 Minutes")
    half_day_cutoff_time = models.CharField(max_length=50, default="01:30 PM")
    shift_start_time = models.CharField(max_length=50, default="09:30 AM")
    shift_end_time = models.CharField(max_length=50, default="06:30 PM")
    standard_work_hours = models.FloatField(default=8.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "HR Attendance Setting"
        verbose_name_plural = "HR Attendance Settings"

    def __str__(self):
        return f"Shift: {self.shift_start_time} - {self.shift_end_time} (Grace: {self.grace_period_label})"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class HRLeaveSetting(models.Model):
    annual_casual_leave = models.IntegerField(default=12)
    annual_sick_leave = models.IntegerField(default=6)
    annual_paid_leave = models.IntegerField(default=18)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "HR Leave Setting"
        verbose_name_plural = "HR Leave Settings"

    def __str__(self):
        return f"Leaves: CL={self.annual_casual_leave}, SL={self.annual_sick_leave}, PL={self.annual_paid_leave}"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class HRNotificationSetting(models.Model):
    whatsapp_daily_punch_summary = models.BooleanField(default=True)
    sms_leave_approval = models.BooleanField(default=True)
    email_leave_notifications = models.BooleanField(default=False)
    admin_whatsapp_number = models.CharField(max_length=50, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "HR Notification Setting"
        verbose_name_plural = "HR Notification Settings"

    def __str__(self):
        return "HR Notification Preferences"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class HRRolePermission(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('STAFF', 'Staff Operator'),
        ('HR', 'HR Manager'),
    ]

    role = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    display_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    can_manage_employees = models.BooleanField(default=False)
    can_view_attendance = models.BooleanField(default=True)
    can_mark_attendance = models.BooleanField(default=True)
    can_approve_leaves = models.BooleanField(default=False)
    can_manage_payroll = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    can_process_services = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "HR Role Permission"
        verbose_name_plural = "HR Role Permissions"
        ordering = ['role']

    def __str__(self):
        return f"{self.role} ({self.display_name or self.get_role_display()})"

    @classmethod
    def seed_defaults(cls):
        defaults = [
            {
                'role': 'ADMIN',
                'display_name': 'Administrator',
                'description': 'Full administrative access to all modules, finance, payroll, and configuration.',
                'can_manage_employees': True,
                'can_view_attendance': True,
                'can_mark_attendance': True,
                'can_approve_leaves': True,
                'can_manage_payroll': True,
                'can_view_reports': True,
                'can_manage_settings': True,
                'can_process_services': True,
            },
            {
                'role': 'STAFF',
                'display_name': 'Front Desk Operator',
                'description': 'Operational intake operator: Citizen service processing and attendance punch-in.',
                'can_manage_employees': False,
                'can_view_attendance': True,
                'can_mark_attendance': True,
                'can_approve_leaves': False,
                'can_manage_payroll': False,
                'can_view_reports': False,
                'can_manage_settings': False,
                'can_process_services': True,
            },
            {
                'role': 'HR',
                'display_name': 'HR Manager',
                'description': 'HR and attendance supervision, leave approval, and staff roster oversight.',
                'can_manage_employees': True,
                'can_view_attendance': True,
                'can_mark_attendance': True,
                'can_approve_leaves': True,
                'can_manage_payroll': False,
                'can_view_reports': True,
                'can_manage_settings': False,
                'can_process_services': False,
            },
        ]
        results = []
        for d in defaults:
            role_val = d.pop('role')
            obj, _ = cls.objects.get_or_create(role=role_val, defaults=d)
            results.append(obj)
        return results
