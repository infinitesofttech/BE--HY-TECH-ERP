from django.db import models
from django.utils import timezone
from django.conf import settings


class BaseService(models.Model):
    CATEGORY_CHOICES = [
        ('GOVT_FORMS', 'Government Forms — Current Services'),
        ('CARD_SERVICES', 'Update / Card Services'),
        ('NEW_SERVICES', 'New Services'),
        ('OTHER_SERVICES', 'Other Center Services'),
        ('COMPUTER_COURSES', 'Computer Courses'),
        ('ADDITIONAL_SERVICES', 'Additional Services'),
    ]

    SERVICE_TYPE_CHOICES = [
        ('NEW', 'New'),
        ('UPDATE', 'Update'),
        ('RENEWAL', 'Renewal'),
        ('KYC', 'KYC'),
        ('OTHER', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    ServiceName = models.CharField(max_length=200)
    ServiceNameGu = models.CharField(max_length=200, blank=True, null=True)
    Category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    SubCategory = models.CharField(max_length=100, blank=True, null=True)
    Department = models.CharField(max_length=200, blank=True, null=True)
    ServiceType = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, default='NEW', blank=True, null=True)
    Description = models.TextField(blank=True, null=True)
    GovernmentFee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ServiceCharge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    TotalFee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SlaDays = models.PositiveIntegerField(default=7)
    Priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    SmsTemplateGu = models.TextField(blank=True, null=True)
    SmsTemplateEn = models.TextField(blank=True, null=True)
    StaffInstructions = models.TextField(blank=True, null=True)
    FormFields = models.JSONField(default=list, blank=True)
    PortalUrl = models.URLField(max_length=500, blank=True, null=True)
    IsOfficial = models.BooleanField(default=True)
    IsActive = models.BooleanField(default=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.id} - {self.ServiceName}"

    def save(self, *args, **kwargs):
        if not self.TotalFee or self.TotalFee == 0:
            self.TotalFee = (self.GovernmentFee or 0) + (self.ServiceCharge or 0)
        super().save(*args, **kwargs)


class SubService(models.Model):
    Service = models.ForeignKey(BaseService, on_delete=models.CASCADE, related_name='sub_services')
    SubServiceName = models.CharField(max_length=200)
    Description = models.TextField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.SubServiceName} ({self.Service.ServiceName})"


class RequiredDocument(models.Model):
    SubService = models.ForeignKey(SubService, on_delete=models.CASCADE, related_name='required_documents')
    DocumentName = models.CharField(max_length=200)
    document_type = models.CharField(max_length=50, default='AADHAR')
    IsRequired = models.BooleanField(default=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.DocumentName} -> {self.SubService.SubServiceName}"


class Transaction(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('CASH', 'Cash'),
        ('ONLINE/UPI', 'Online / UPI'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('WALLET', 'Wallet'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('ONLINE', 'Online'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
        ('PENDING', 'Pending'),
    ]

    transaction_no = models.CharField(max_length=50, unique=True, db_index=True)
    transaction_date = models.DateField(default=timezone.now)
    customer = models.ForeignKey('hytech_customers.Customer', on_delete=models.CASCADE, related_name='transactions')
    service = models.ForeignKey(BaseService, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    sub_service = models.ForeignKey(SubService, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_transactions')
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PAID')
    payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODE_CHOICES, default='CASH')
    points_earned = models.IntegerField(default=0)
    employee_points = models.IntegerField(default=0)
    points_redeemed = models.IntegerField(default=0)
    wallet_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    wallet_used = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_wallet_change = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    previous_due_cleared = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remarks = models.TextField(blank=True, null=True)
    items = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_no} - ₹{self.bill_amount}"

    def save(self, *args, **kwargs):
        if not self.transaction_no:
            last = Transaction.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.transaction_no = f"TXN-{next_num:06d}"
        super().save(*args, **kwargs)
