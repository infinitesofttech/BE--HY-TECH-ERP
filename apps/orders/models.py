from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    dealer = models.ForeignKey(
        'masters.Dealer',
        on_delete=models.CASCADE,
        related_name='orders',
    )
    client = models.CharField(max_length=200, blank=True)
    order_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} - {self.employee}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.product} x{self.quantity}'

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('sent', 'Sent'), ('accepted', 'Accepted'),
        ('rejected', 'Rejected'), ('expired', 'Expired'),
    ]
    PAYMENT_TERMS_CHOICES = [
        ('advance', 'Advance'),
        ('due_on_receipt', 'Due on Receipt'),
        ('net_7', 'Net 7'),
        ('net_15', 'Net 15'),
        ('net_30', 'Net 30'),
        ('net_45', 'Net 45'),
        ('net_60', 'Net 60'),
        ('cogd', 'Cash on Goods Delivery'),
    ]

    quote_id = models.CharField(max_length=50, unique=True, blank=True)
    client = models.CharField(max_length=200)
    lead = models.ForeignKey(
        'pipeline.Lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations',
        help_text='Lead this quotation originated from.',
    )
    customer = models.ForeignKey(
        'sales.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations',
        help_text='Customer record linked to this quotation.',
    )
    quote_date = models.DateField(null=True, blank=True)
    valid_till = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    payment_terms = models.CharField(
        max_length=20, choices=PAYMENT_TERMS_CHOICES, default='net_30',
    )
    tax = models.ForeignKey(
        'finance.Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='quotations',
        help_text='GST / tax applied to the subtotal.',
    )
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quotations',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.quote_id

    def save(self, *args, **kwargs):
        if not self.quote_id:
            super().save(*args, **kwargs)
            self.quote_id = f'QOT{self.pk:04d}'
            super().save(update_fields=['quote_id'])
        else:
            super().save(*args, **kwargs)

    @property
    def tax_percentage(self):
        from decimal import Decimal
        return self.tax.rate if self.tax else Decimal('0')

    @property
    def tax_name(self):
        return self.tax.name if self.tax else None

    def recalculate_totals(self):
        from django.db.models import Sum
        from decimal import Decimal
        subtotal = self.items.aggregate(total=Sum('amount'))['total'] or 0
        self.total_amount = subtotal
        self.gst_amount = subtotal * self.tax_percentage / Decimal('100')
        self.final_amount = (
            subtotal - self.discount + self.gst_amount + self.shipping_charge
        )
        self.save(update_fields=[
            'total_amount', 'gst_amount', 'final_amount',
        ])
        return self.final_amount


class QuotationItem(models.Model):
    quotation = models.ForeignKey(
        Quotation, on_delete=models.CASCADE, related_name='items',
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL, null=True, blank=True,
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text='Discount in %',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.product} x{self.quantity}'

    def save(self, *args, **kwargs):
        if self.discount >= 100:
            self.amount = 0
        else:
            self.amount = self.quantity * self.price * (1 - self.discount / 100)
        super().save(*args, **kwargs)
