from datetime import date
from decimal import Decimal

from django.db import models, transaction
from django.db.models import Sum
from django.utils.text import slugify


class ProductCategory(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Product Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('two_wheeler', 'Two Wheeler'),
        ('four_wheeler', 'Four Wheeler'),
        ('both', 'Both'),
    ]
    AVAILABILITY_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('limited', 'Limited'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
    )
    sku = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    specifications = models.JSONField(default=dict, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.ForeignKey(
        'finance.Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
        help_text='Tax applied to this product.',
    )
    unit = models.CharField(max_length=50, blank=True, default='piece')
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default='in_stock'
    )
    for_vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        default='both',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def tax_percentage(self):
        return self.tax.rate if self.tax else Decimal('0')

    @property
    def tax_name(self):
        return self.tax.name if self.tax else None

    def __str__(self):
        return self.name


class TourPlan(models.Model):
    TOUR_TYPE_CHOICES = [
        ('two_wheeler', 'Two Wheeler'),
        ('four_wheeler', 'Four Wheeler'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tour_type = models.CharField(max_length=20, choices=TOUR_TYPE_CHOICES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration_days = models.IntegerField(default=1)
    plan_details = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Policy(models.Model):
    CATEGORY_CHOICES = [
        ('travel', 'Travel'),
        ('leave', 'Leave'),
        ('sales', 'Sales'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    attachment = models.FileField(
        upload_to='policies/', null=True, blank=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Warehouse(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Inventory(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_items',
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='inventory_items',
    )
    quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Inventories'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name} - {self.warehouse.name} ({self.quantity})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        sync_product_quantity(self.product)

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        sync_product_quantity(product)


def sync_product_quantity(product):
    total = Inventory.objects.filter(
        product=product, status='active',
    ).aggregate(total=Sum('quantity'))['total'] or 0
    Product.objects.filter(pk=product.pk).update(quantity=total)


def adjust_inventory(product, warehouse, delta):
    with transaction.atomic():
        inventory = Inventory.objects.select_for_update().filter(
            product=product, warehouse=warehouse,
        ).first()
        if delta < 0:
            available = inventory.quantity if inventory else 0
            if available + delta < 0:
                raise ValueError(
                    f'Insufficient stock in {warehouse.name}. '
                    f'Available: {available}, requested change: {delta}.'
                )
        if inventory is None:
            inventory = Inventory(
                product=product, warehouse=warehouse, quantity=0,
                status='active',
            )
        inventory.quantity += delta
        inventory.save()
    return inventory


class StockAdjustment(models.Model):
    REASON_CHOICES = [
        ('damaged', 'Damaged'),
        ('miscount', 'Miscount'),
        ('transfer', 'Transfer'),
        ('lost', 'Lost'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_adjustments',
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stock_adjustments',
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    difference = models.IntegerField(
        help_text='Positive value increases stock, negative value decreases it.',
    )
    adjustment_date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-adjustment_date', '-created_at']

    def save(self, *args, **kwargs):
        old = None
        if self.pk:
            try:
                old = StockAdjustment.objects.get(pk=self.pk)
            except StockAdjustment.DoesNotExist:
                pass
        with transaction.atomic():
            if old is not None:
                adjust_inventory(old.product, old.warehouse, -old.difference)
            super().save(*args, **kwargs)
            adjust_inventory(self.product, self.warehouse, self.difference)

    def __str__(self):
        sign = '+' if self.difference >= 0 else ''
        return f'{self.product.name} ({self.warehouse.name}) {sign}{self.difference}'


class StockTransfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('in_transit', 'In Transit'),
        ('complete', 'Complete'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_transfers',
    )
    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='outgoing_stock_transfers',
    )
    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='incoming_stock_transfers',
    )
    quantity = models.PositiveIntegerField()
    transfer_date = models.DateField(default=date.today)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transfer_date', '-created_at']

    def __str__(self):
        return f'{self.product.name}: {self.from_warehouse.name} -> {self.to_warehouse.name} ({self.status})'

    def save(self, *args, **kwargs):
        old_status = 'pending'
        if self.pk:
            try:
                old_status = StockTransfer.objects.get(pk=self.pk).status
            except StockTransfer.DoesNotExist:
                pass
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.apply_status_transition(old_status)

    @transaction.atomic
    def apply_status_transition(self, old_status):
        old_deducted = old_status in ('in_transit', 'complete')
        new_deducted = self.status in ('in_transit', 'complete')
        old_added = old_status == 'complete'
        new_added = self.status == 'complete'

        if not old_deducted and new_deducted:
            adjust_inventory(self.product, self.from_warehouse, -self.quantity)
        elif old_deducted and not new_deducted:
            adjust_inventory(self.product, self.from_warehouse, self.quantity)

        if not old_added and new_added:
            adjust_inventory(self.product, self.to_warehouse, self.quantity)
        elif old_added and not new_added:
            adjust_inventory(self.product, self.to_warehouse, -self.quantity)

    def reverse_stock(self):
        with transaction.atomic():
            if self.status == 'complete':
                adjust_inventory(self.product, self.to_warehouse, -self.quantity)
                adjust_inventory(self.product, self.from_warehouse, self.quantity)
            elif self.status == 'in_transit':
                adjust_inventory(self.product, self.from_warehouse, self.quantity)
