from django.db import models
from django.utils import timezone
from django.conf import settings


class Reminder(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    ]

    reminder_no = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey('hytech_customers.Customer', on_delete=models.CASCADE, related_name='reminders')
    service = models.ForeignKey('hytech_services.BaseService', on_delete=models.SET_NULL, null=True, blank=True, related_name='reminders')
    reminder_type = models.CharField(max_length=50, default='SERVICE_READY')
    subject = models.CharField(max_length=200)
    due_date = models.DateField()
    reminder_date = models.DateField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    message_template = models.TextField(blank=True, null=True)
    follow_up_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    last_contact_date = models.DateTimeField(null=True, blank=True)
    customer_response = models.TextField(blank=True, null=True)
    next_follow_up = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_reminders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reminder_no} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.reminder_no:
            last = Reminder.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.reminder_no = f"RMD-{next_num:06d}"
        super().save(*args, **kwargs)


class FollowUp(models.Model):
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, related_name='follow_ups')
    contact_date = models.CharField(max_length=100)
    customer_response = models.TextField()
    next_follow_up = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    contacted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='logged_follow_ups')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"FollowUp on {self.reminder.reminder_no} at {self.contact_date}"


class PendingWork(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('BLOCKED', 'Blocked'),
        ('COMPLETED', 'Completed'),
    ]

    pending_no = models.CharField(max_length=50, unique=True, db_index=True)
    service_visit = models.ForeignKey('hytech_customers.ServiceVisit', on_delete=models.SET_NULL, null=True, blank=True, related_name='pending_works')
    customer = models.ForeignKey('hytech_customers.Customer', on_delete=models.CASCADE, related_name='pending_works')
    service = models.ForeignKey('hytech_services.BaseService', on_delete=models.SET_NULL, null=True, blank=True, related_name='pending_works')
    pending_since = models.DateField(default=timezone.localdate)
    expected_date = models.DateField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    pending_reason = models.TextField()
    documents_pending = models.TextField(blank=True, null=True)
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_pending_works')
    next_action = models.TextField(blank=True, null=True)
    work_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_pending_works')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.pending_no} - {self.customer.head_of_family}"

    def save(self, *args, **kwargs):
        if not self.pending_no:
            last = PendingWork.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.pending_no = f"PW-{next_num:06d}"
        super().save(*args, **kwargs)


class Application(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('DOCUMENT_CHECK', 'Document Check'),
        ('READY_TO_SUBMIT', 'Ready to Submit'),
        ('SUBMITTED', 'Submitted'),
        ('GOVERNMENT_PROCESSING', 'Government Processing'),
        ('PENDING', 'Pending'),
        ('ACTION_REQUIRED', 'Action Required'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
        ('SCRUTINY', 'Scrutiny'),
        ('DOCS_PENDING', 'Documents Pending'),
    ]

    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('URGENT', 'Urgent'),
    ]

    application_no = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey('hytech_customers.Customer', on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    family_member = models.ForeignKey('hytech_customers.FamilyMember', on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    applicant_name = models.CharField(max_length=200, blank=True)
    applicant_mobile = models.CharField(max_length=20, blank=True)
    service = models.ForeignKey('hytech_services.BaseService', on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    sub_service = models.ForeignKey('hytech_services.SubService', on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    category = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='DRAFT')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NORMAL')
    government_app_no = models.CharField(max_length=100, blank=True, null=True)
    government_portal_url = models.URLField(max_length=500, blank=True, null=True)
    govt_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, default='PAID')
    payment_mode = models.CharField(max_length=30, blank=True, null=True)
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_applications')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_applications')
    expected_date = models.DateField(null=True, blank=True)
    sla_days = models.PositiveIntegerField(default=7)
    documents = models.JSONField(default=list, blank=True)
    form_data = models.JSONField(default=dict, blank=True)
    timeline = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.application_no} - {self.applicant_name or (self.customer and self.customer.head_of_family)}"

    def save(self, *args, **kwargs):
        if not self.application_no:
            last = Application.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.application_no = f"APP-{next_num:06d}"
        super().save(*args, **kwargs)
