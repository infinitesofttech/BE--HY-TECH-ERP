from django.conf import settings
from django.db import models


class Payroll(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    ]

    payroll_no = models.CharField(max_length=20, unique=True, editable=False)
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payrolls',
        help_text='Employee this payroll belongs to.',
    )
    payroll_month = models.CharField(
        max_length=7, help_text='Payroll month in YYYY-MM format.',
    )
    basic_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hra = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='House Rent Allowance (20% of basic pay).',
    )
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pf = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Provident Fund deduction.',
    )
    net_monthly = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Net monthly = basic + HRA + allowances - PF.',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Payrolls'

    def __str__(self):
        return f'{self.payroll_no} - {self.employee.get_full_name() or self.employee.username} - {self.payroll_month}'

    def compute(self):
        self.net_monthly = (
            self.basic_pay + self.hra + self.allowances - self.pf
        )

    def save(self, *args, **kwargs):
        self.compute()
        if not self.payroll_no:
            last = Payroll.objects.select_for_update().order_by('-id').first()
            if last:
                try:
                    last_number = int(last.payroll_no.split('-')[1])
                except (IndexError, ValueError):
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1
            self.payroll_no = f"PL-{new_number:06d}"
        super().save(*args, **kwargs)


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('PORTAL_WALLET_CHARGE', 'Portal Wallet Charge'),
        ('OFFICE_SUPPLIES', 'Office Supplies'),
        ('ELECTRICITY', 'Electricity'),
        ('INTERNET', 'Internet'),
        ('HARDWARE_MAINTENANCE', 'Hardware Maintenance'),
        ('OTHER', 'Other Expense'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('ONLINE', 'Online'),
        ('CASH', 'Cash'),
    ]

    expense_no = models.CharField(max_length=20, unique=True, editable=False)
    expense_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='OTHER')
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODE_CHOICES, default='CASH')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)
    expense_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f'{self.expense_no} - {self.expense_name}'

    def save(self, *args, **kwargs):
        if not self.expense_no:
            last = Expense.objects.select_for_update().order_by('-id').first()
            if last:
                try:
                    last_number = int(last.expense_no.split('-')[1])
                except (IndexError, ValueError):
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1
            self.expense_no = f"EXP-{new_number:06d}"
        super().save(*args, **kwargs)
