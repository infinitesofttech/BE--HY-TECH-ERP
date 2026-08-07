from django.conf import settings
from django.db import models


class AssetRegistration(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    asset_name = models.CharField(max_length=200)
    asset_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_assets',
    )
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField()
    warranty_end_date = models.DateField(null=True, blank=True)
    warranty = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Warranty duration in months.',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.asset_name


class AssetAssignment(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    assignment_id = models.CharField(max_length=20, unique=True, blank=True)
    asset = models.ForeignKey(
        AssetRegistration,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_assignments',
    )
    department = models.CharField(max_length=100, blank=True)
    assignment_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.assignment_id} - {self.asset.asset_name}'

    def save(self, *args, **kwargs):
        if not self.assignment_id:
            super().save(*args, **kwargs)
            self.assignment_id = f'ASN-{self.pk:04d}'
            super().save(update_fields=['assignment_id'])
            return
        super().save(*args, **kwargs)


class AssetDepreciation(models.Model):
    METHOD_CHOICES = [
        ('declining_balance', 'Declining Balance'),
        ('straight_line', 'Straight Line'),
        ('units_of_production', 'Units of Production'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
        ('in_use', 'In Use'),
    ]

    depreciation_id = models.CharField(max_length=20, unique=True, blank=True)
    asset = models.ForeignKey(
        AssetRegistration,
        on_delete=models.CASCADE,
        related_name='depreciations',
    )
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2)
    accumulated_depreciation = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    net_book_value = models.DecimalField(max_digits=12, decimal_places=2)
    depreciation_method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, default='straight_line',
    )
    useful_life_years = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.depreciation_id} - {self.asset.asset_name}'

    def save(self, *args, **kwargs):
        if not self.depreciation_id:
            super().save(*args, **kwargs)
            self.depreciation_id = f'DEP-{self.pk:04d}'
            super().save(update_fields=['depreciation_id'])
            return
        super().save(*args, **kwargs)


class AssetMaintenance(models.Model):
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
    ]
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('scheduled', 'Scheduled'),
        ('pending', 'Pending'),
    ]

    maintenance_id = models.CharField(max_length=20, unique=True, blank=True)
    asset = models.ForeignKey(
        AssetRegistration,
        on_delete=models.CASCADE,
        related_name='maintenances',
    )
    maintenance_type = models.CharField(
        max_length=20, choices=MAINTENANCE_TYPE_CHOICES, default='preventive',
    )
    scheduled_date = models.DateField()
    remark = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.maintenance_id} - {self.asset.asset_name}'

    def save(self, *args, **kwargs):
        if not self.maintenance_id:
            super().save(*args, **kwargs)
            self.maintenance_id = f'MNT-{self.pk:04d}'
            super().save(update_fields=['maintenance_id'])
            return
        super().save(*args, **kwargs)


class AssetDisposal(models.Model):
    METHOD_CHOICES = [
        ('sold', 'Sold'),
        ('scrapped', 'Scrapped'),
        ('auction', 'Auction'),
        ('recycle', 'Recycle'),
    ]
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('scheduled', 'Scheduled'),
    ]

    disposal_id = models.CharField(max_length=20, unique=True, blank=True)
    asset = models.ForeignKey(
        AssetRegistration,
        on_delete=models.CASCADE,
        related_name='disposals',
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='sold')
    value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_disposals',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.disposal_id} - {self.asset.asset_name}'

    def save(self, *args, **kwargs):
        if not self.disposal_id:
            super().save(*args, **kwargs)
            self.disposal_id = f'DSP-{self.pk:04d}'
            super().save(update_fields=['disposal_id'])
            return
        super().save(*args, **kwargs)
