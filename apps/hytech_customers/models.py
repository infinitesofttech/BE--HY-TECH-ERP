from django.db import models
from django.utils import timezone
from django.conf import settings


class Customer(models.Model):
    family_id = models.CharField(max_length=50, unique=True, db_index=True)
    registration_date = models.DateField(default=timezone.now)
    head_of_family = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=20, db_index=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    family_member_count = models.PositiveIntegerField(default=1)
    village_city = models.CharField(max_length=200, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    referral_family_id = models.CharField(max_length=50, blank=True, null=True)
    document_consent = models.BooleanField(default=True)
    current_points = models.IntegerField(default=0)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_visits = models.PositiveIntegerField(default=0)
    last_visit = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    digital_card_sent = models.BooleanField(default=False)
    password = models.CharField(max_length=128, blank=True, default='', help_text="Encrypted password for Citizen Portal login")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.family_id} - {self.head_of_family}"

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        if not self.password:
            return False
        if self.password.startswith(('pbkdf2_', 'argon2', 'bcrypt')):
            return check_password(raw_password, self.password)
        if self.password == raw_password:
            self.set_password(raw_password)
            self.save(update_fields=['password'])
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.family_id:
            last = Customer.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.family_id = f"HTF-{next_num:06d}"
        super().save(*args, **kwargs)


class FamilyMember(models.Model):
    RELATIONSHIP_CHOICES = [
        ('HEAD', 'Head of Family'),
        ('SELF', 'Self'),
        ('WIFE', 'Wife'),
        ('HUSBAND', 'Husband'),
        ('SON', 'Son'),
        ('DAUGHTER', 'Daughter'),
        ('FATHER', 'Father'),
        ('MOTHER', 'Mother'),
        ('BROTHER', 'Brother'),
        ('SISTER', 'Sister'),
        ('OTHER', 'Other'),
    ]
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='members')
    family_id = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES, default='OTHER')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='MALE')
    mobile_number = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.family_id}"

    def save(self, *args, **kwargs):
        if self.customer and not self.family_id:
            self.family_id = self.customer.family_id
        super().save(*args, **kwargs)


class CustomerDocument(models.Model):
    DOCUMENT_TYPES = [
        ('AADHAR', 'Aadhaar Card'),
        ('VOTER_ID', 'Voter ID / Election Card'),
        ('PAN', 'PAN Card'),
        ('RATION_CARD', 'Ration Card'),
        ('BIRTH_CERTIFICATE', 'Birth Certificate'),
        ('CASTE_CERTIFICATE', 'Caste Certificate'),
        ('INCOME_CERTIFICATE', 'Income Certificate'),
        ('DRIVING_LICENSE', 'Driving License'),
        ('PHOTO', 'Passport Photo'),
        ('OTHER', 'Other Document'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    family_member = models.ForeignKey(FamilyMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    family_id = models.CharField(max_length=50, blank=True)
    member_name = models.CharField(max_length=200, blank=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_name = models.CharField(max_length=255)
    document_file = models.FileField(upload_to='customer_documents/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.document_name} ({self.document_type}) - {self.family_id}"

    def save(self, *args, **kwargs):
        if self.customer and not self.family_id:
            self.family_id = self.customer.family_id
        if self.family_member and not self.member_name:
            self.member_name = self.family_member.name
        super().save(*args, **kwargs)


class ServiceVisit(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    visit_no = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='service_visits')
    family_member = models.ForeignKey(FamilyMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_visits')
    service = models.ForeignKey('hytech_services.BaseService', on_delete=models.SET_NULL, null=True, blank=True, related_name='visits')
    sub_service = models.ForeignKey('hytech_services.SubService', on_delete=models.SET_NULL, null=True, blank=True, related_name='visits')
    checked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_visits')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    visit_date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.visit_no} - {self.customer.head_of_family}"

    def save(self, *args, **kwargs):
        if not self.visit_no:
            last = ServiceVisit.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.visit_no = f"VIS-{next_num:06d}"
        super().save(*args, **kwargs)


class VisitDocument(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('NOT_AVAILABLE', 'Not Available'),
    ]

    visit = models.ForeignKey(ServiceVisit, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50)
    document_name = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='NOT_AVAILABLE')
    document_file = models.FileField(upload_to='visit_documents/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.document_name} [{self.status}]"
