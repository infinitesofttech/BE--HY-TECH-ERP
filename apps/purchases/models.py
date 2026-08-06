from decimal import Decimal

from django.db import models
from django.db.models import F, Sum
from django.conf import settings


class Vendor(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Purchase(models.Model):
    PAYMENT_TERMS_CHOICES = [
        ('due_on_receipt', 'Due on Receipt'),
        ('net_7', 'Net 7'),
        ('net_15', 'Net 15'),
        ('net_30', 'Net 30'),
        ('net_45', 'Net 45'),
        ('net_60', 'Net 60'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
    ]

    purchase_id = models.CharField(max_length=20, unique=True, blank=True)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='purchases',
    )
    requestor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='purchases',
        help_text='Employee who requested the purchase.',
    )
    company_logo = models.ImageField(
        upload_to='purchases/', null=True, blank=True,
    )
    company_from = models.TextField(blank=True)
    company_to = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    payment_terms = models.CharField(
        max_length=20, choices=PAYMENT_TERMS_CHOICES, default='net_30',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
    )
    tax = models.ForeignKey(
        'finance.Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='purchases',
        help_text='Tax applied to the subtotal.',
    )
    total_discount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    shipping_charge = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return self.purchase_id or f'Purchase {self.pk}'

    def save(self, *args, **kwargs):
        if not self.purchase_id:
            super().save(*args, **kwargs)
            self.purchase_id = f'PC-{self.pk:04d}'
            super().save(update_fields=['purchase_id'])
            return
        super().save(*args, **kwargs)

    @property
    def tax_percentage(self):
        return self.tax.rate if self.tax else Decimal('0')

    @property
    def tax_name(self):
        return self.tax.name if self.tax else None

    def recalculate_total(self):
        agg = self.items.aggregate(subtotal=Sum('amount'))
        subtotal = agg['subtotal'] or 0
        tax_amount = subtotal * self.tax_percentage / Decimal('100')
        self.total_amount = (
            subtotal - self.total_discount + tax_amount + self.shipping_charge
        )
        self.save(update_fields=['total_amount'])
        return self.total_amount


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.product} x{self.quantity}'

    def save(self, *args, **kwargs):
        self.amount = (self.quantity * self.unit_price) - self.discount
        super().save(*args, **kwargs)


class PurchaseOrder(models.Model):
    PAYMENT_TERMS_CHOICES = Purchase.PAYMENT_TERMS_CHOICES
    STATUS_CHOICES = Purchase.STATUS_CHOICES

    purchase_order_id = models.CharField(max_length=20, unique=True, blank=True)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='purchase_orders',
    )
    company_logo = models.ImageField(
        upload_to='purchases/orders/', null=True, blank=True,
    )
    company_from = models.TextField(blank=True)
    company_to = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    payment_terms = models.CharField(
        max_length=20, choices=PAYMENT_TERMS_CHOICES, default='net_30',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
    )
    tax = models.ForeignKey(
        'finance.Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='purchase_orders',
        help_text='Tax applied to the subtotal.',
    )
    total_discount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    shipping_charge = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date', '-created_at']

    def __str__(self):
        return self.purchase_order_id or f'PurchaseOrder {self.pk}'

    def save(self, *args, **kwargs):
        if not self.purchase_order_id:
            super().save(*args, **kwargs)
            self.purchase_order_id = f'PO-{self.pk:04d}'
            super().save(update_fields=['purchase_order_id'])
            return
        super().save(*args, **kwargs)

    @property
    def tax_percentage(self):
        return self.tax.rate if self.tax else Decimal('0')

    @property
    def tax_name(self):
        return self.tax.name if self.tax else None

    def recalculate_total(self):
        agg = self.items.aggregate(subtotal=Sum('amount'))
        subtotal = agg['subtotal'] or 0
        tax_amount = subtotal * self.tax_percentage / Decimal('100')
        self.total_amount = (
            subtotal - self.total_discount + tax_amount + self.shipping_charge
        )
        self.save(update_fields=['total_amount'])
        return self.total_amount


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.product} x{self.quantity}'

    def save(self, *args, **kwargs):
        self.amount = (self.quantity * self.unit_price) - self.discount
        super().save(*args, **kwargs)


class PurchaseReturn(models.Model):
    PAYMENT_TERMS_CHOICES = Purchase.PAYMENT_TERMS_CHOICES
    STATUS_CHOICES = Purchase.STATUS_CHOICES

    return_id = models.CharField(max_length=20, unique=True, blank=True)
    purchase = models.ForeignKey(
        Purchase,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='returns',
        help_text='Optional reference to the original purchase.',
    )
    vendor = models.ForeignKey(
        Vendor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='purchase_returns',
    )
    company_logo = models.ImageField(
        upload_to='purchases/returns/', null=True, blank=True,
    )
    company_from = models.TextField(blank=True)
    company_to = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    return_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
    )
    return_reason = models.TextField(blank=True)
    tax = models.ForeignKey(
        'finance.Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='purchase_returns',
        help_text='Tax applied to the subtotal.',
    )
    total_discount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    shipping_charge = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-return_date', '-created_at']

    def __str__(self):
        return self.return_id or f'PurchaseReturn {self.pk}'

    def save(self, *args, **kwargs):
        if not self.vendor_id and self.purchase_id:
            self.vendor = self.purchase.vendor
        if not self.return_id:
            super().save(*args, **kwargs)
            self.return_id = f'PR-{self.pk:04d}'
            super().save(update_fields=['return_id'])
            return
        super().save(*args, **kwargs)

    @property
    def tax_percentage(self):
        return self.tax.rate if self.tax else Decimal('0')

    @property
    def tax_name(self):
        return self.tax.name if self.tax else None

    def recalculate_total(self):
        agg = self.items.aggregate(subtotal=Sum('amount'))
        subtotal = agg['subtotal'] or 0
        tax_amount = subtotal * self.tax_percentage / Decimal('100')
        self.total_amount = (
            subtotal - self.total_discount + tax_amount + self.shipping_charge
        )
        self.save(update_fields=['total_amount'])
        return self.total_amount


class PurchaseReturnItem(models.Model):
    purchase_return = models.ForeignKey(
        PurchaseReturn,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.product} x{self.quantity}'

    def save(self, *args, **kwargs):
        self.amount = (self.quantity * self.unit_price) - self.discount
        super().save(*args, **kwargs)
