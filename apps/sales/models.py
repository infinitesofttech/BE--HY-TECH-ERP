from decimal import Decimal

from django.db import models
from django.db.models import F, Sum
from django.conf import settings


class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SalesOrder(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    quotation = models.ForeignKey(
        'orders.Quotation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_orders',
        help_text='Quotation that was approved to create this order.',
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sales_orders',
        help_text='Sales rep responsible for the order.',
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='sales_orders',
    )
    company_logo = models.ImageField(
        upload_to='sales/orders/', null=True, blank=True,
    )
    company_from = models.TextField(
        blank=True, help_text='Company / from address',
    )
    company_to = models.TextField(
        blank=True, help_text='Customer / to address',
    )
    date = models.DateField()
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_progress',
    )
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return self.order_id or f'SalesOrder {self.pk}'

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = None
            super().save(*args, **kwargs)
            self.order_id = f'SO-{self.pk:04d}'
            super().save(update_fields=['order_id'])
            return
        super().save(*args, **kwargs)

    def recalculate_total(self):
        agg = self.items.aggregate(
            subtotal=Sum(F('amount') + F('tax_amount')),
        )
        self.total_amount = (
            (agg['subtotal'] or 0) - self.total_discount + self.shipping_charge
        )
        self.save(update_fields=['total_amount'])
        return self.total_amount


class SalesOrderItem(models.Model):
    order = models.ForeignKey(
        SalesOrder,
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
    tax = models.ForeignKey(
        'finance.Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sales_order_items',
        help_text='Tax applied to the line amount.',
    )
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.product} x{self.quantity}'

    @property
    def tax_percentage(self):
        return self.tax.rate if self.tax else Decimal('0')

    @property
    def tax_name(self):
        return self.tax.name if self.tax else None

    def save(self, *args, **kwargs):
        self.amount = (self.quantity * self.unit_price) - self.discount
        self.tax_amount = self.amount * self.tax_percentage / Decimal('100')
        super().save(*args, **kwargs)


class Refund(models.Model):
    PAYMENT_METHOD_CHOICES = SalesOrder.PAYMENT_METHOD_CHOICES
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('proceed', 'Proceed'),
        ('rejected', 'Rejected'),
    ]

    refund_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='refunds',
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
    )
    refund_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.refund_id or f'Refund {self.pk}'

    def save(self, *args, **kwargs):
        if not self.refund_id:
            self.refund_id = None
            super().save(*args, **kwargs)
            self.refund_id = f'RF-{self.pk:04d}'
            super().save(update_fields=['refund_id'])
            return
        super().save(*args, **kwargs)


class DeliveryNote(models.Model):
    FREQUENCY_CHOICES = [
        ('once', 'Once'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    delivery_note_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_notes',
        help_text='Sales order this delivery note fulfils.',
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='delivery_notes',
    )
    company_logo = models.ImageField(
        upload_to='sales/delivery_notes/', null=True, blank=True,
    )
    company_from = models.TextField(blank=True)
    company_to = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    frequency = models.CharField(
        max_length=20, choices=FREQUENCY_CHOICES, default='once',
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active',
    )
    note = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    tax = models.ForeignKey(
        'finance.Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='delivery_notes',
        help_text='Tax applied to the subtotal.',
    )
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-invoice_date', '-created_at']

    def __str__(self):
        return self.delivery_note_id or f'DeliveryNote {self.pk}'

    def save(self, *args, **kwargs):
        if not self.delivery_note_id:
            self.delivery_note_id = None
            super().save(*args, **kwargs)
            self.delivery_note_id = f'DN-{self.pk:04d}'
            super().save(update_fields=['delivery_note_id'])
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


class DeliveryNoteItem(models.Model):
    delivery_note = models.ForeignKey(
        DeliveryNote,
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


class CustomerFeedback(models.Model):
    STATUS_CHOICES = [
        ('resolved', 'Resolved'),
        ('in_review', 'In Review'),
        ('pending', 'Pending'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    subject = models.CharField(max_length=200)
    feedback = models.TextField()
    date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.customer.name} - {self.subject}'
