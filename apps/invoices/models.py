from decimal import Decimal

from django.db import models
from django.conf import settings


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid'),
        ('overdue', 'Overdue'), ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'), ('cheque', 'Cheque'), ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online'), ('other', 'Other'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text='Sales order this invoice bills for.',
    )
    delivery_note = models.ForeignKey(
        'sales.DeliveryNote',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text='Delivery note this invoice was raised from.',
    )
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True)
    customer_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    company = models.ForeignKey(
        'contacts.Company', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='invoices',
        help_text='Registered company this invoice is connected to.',
    )
    invoice_date = models.DateField()
    due_date = models.DateField()
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash'
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.ForeignKey(
        'finance.Tax',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='invoices',
    )
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def tax_percentage(self):
        return self.tax.rate if self.tax else Decimal('0')

    @property
    def tax_name(self):
        return self.tax.name if self.tax else None

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = None
            super().save(*args, **kwargs)
            self.invoice_number = f'INV-{self.pk:04d}'
            super().save(update_fields=['invoice_number'])
            return
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='items'
    )
    description = models.CharField(max_length=500)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.description} x {self.quantity}'


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'), ('cheque', 'Cheque'), ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online'), ('other', 'Other'),
    ]
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.invoice.invoice_number} - {self.amount}'
