from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('manager', 'Manager'),
        ('msr', 'MSR'),
        ('dealer', 'Dealer'),
        ('retailer', 'Retailer'),
        ('company', 'Company'),
        ('hr', 'HR'),
        ('accountant', 'Accountant'),
        ('sales_executive', 'Sales Executive'),
        ('marketing_executive', 'Marketing Executive'),
        ('developer', 'Developer'),
        ('support_executive', 'Support Executive'),
        ('operation_executive', 'Operations Executive'),
        ('project_manager', 'Project Manager'),
        ('quality_analyst', 'Quality Analyst'),
        ('designer', 'Designer'),
        ('production_worker', 'Production Worker'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    territory = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=10, blank=True)
    manager = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subordinates',
    )
    device_token = models.CharField(max_length=500, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        'settings_config.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employees',
        help_text='Department this employee belongs to.',
    )
    designation = models.ForeignKey(
        'settings_config.Designation',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employees',
        help_text='Designation / job title of this employee.',
    )
    shift_start_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Work shift start time for this employee.',
    )
    shift_end_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Work shift end time for this employee.',
    )
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = 'Users'
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='unique_user_email',
                condition=models.Q(email__gt=''),
            ),
        ]

    def __str__(self):
        return self.email if self.email else self.username


class ContactInfo(models.Model):
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    working_hours = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Contact Info'
        verbose_name_plural = 'Contact Info'

    def __str__(self):
        return f'Contact Info - {self.phone}'

    def save(self, *args, **kwargs):
        if not self.pk and ContactInfo.objects.exists():
            raise ValueError('Only one ContactInfo instance is allowed.')
        super().save(*args, **kwargs)


class Feedback(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Feedbacks'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.created_at}'


class DeleteAccountRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delete_requests')
    reason = models.TextField()
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {"processed" if self.is_processed else "pending"}'


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.JSONField(default=list, blank=True, help_text='List of permission keys')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class LoginLog(models.Model):
    STATUS_CHOICES = [('success', 'Success'), ('failed', 'Failed')]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='login_logs',
    )
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_duration = models.PositiveIntegerField(default=0, help_text='Duration in seconds')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='success')

    class Meta:
        ordering = ['-login_time']

    def __str__(self):
        return f'{self.user} - {self.login_time} - {self.status}'


class UserActivityLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs',
    )
    action = models.CharField(max_length=200)
    module = models.CharField(max_length=100, blank=True)
    record_id = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-action_date']

    def __str__(self):
        return f'{self.user} - {self.action} - {self.action_date}'


class DesignDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('cad', 'CAD Drawing'),
        ('technical', 'Technical Drawing'),
        ('mockup', 'Mockup'),
        ('flow', 'Flow Diagram'),
        ('other', 'Other'),
    ]

    design_no = models.CharField(max_length=20, unique=True, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='other',
    )
    version = models.CharField(max_length=20, default='1.0')
    file = models.FileField(upload_to='designs/')
    thumbnail = models.ImageField(upload_to='designs/thumbnails/', null=True, blank=True)
    designer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='design_documents',
        help_text='Designer who uploaded this design.',
    )
    visible_to = models.ManyToManyField(
        'settings_config.Department',
        blank=True,
        related_name='visible_designs',
        help_text='Departments allowed to view this design.',
    )
    is_public = models.BooleanField(
        default=False,
        help_text='If true, visible to all departments.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.design_no or self.pk} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.design_no:
            self.design_no = None
            super().save(*args, **kwargs)
            self.design_no = f'DSGN-{self.pk:04d}'
            super().save(update_fields=['design_no'])
            return
        super().save(*args, **kwargs)
