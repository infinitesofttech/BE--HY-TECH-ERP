from django.db import models


class Village(models.Model):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    name_gu = models.CharField(max_length=200, blank=True)
    taluka = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    total_families = models.PositiveIntegerField(default=0)
    total_citizens = models.PositiveIntegerField(default=0)
    total_documents = models.PositiveIntegerField(default=0)
    male_count = models.PositiveIntegerField(default=0)
    female_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.taluka})"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Village.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.code = f"VIL-{next_num:03d}"
        if not self.name_gu:
            self.name_gu = self.name
        super().save(*args, **kwargs)


class ContactInquiry(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONTACTED', 'Contacted'),
        ('RESOLVED', 'Resolved'),
    ]

    full_name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    service_interest = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='NEW')
    assigned_to = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.mobile_number}) - [{self.status}]"


class AuditLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=200)
    user_role = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    details = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} | {self.user_name} | {self.action} | {self.entity_type} #{self.entity_id}"
