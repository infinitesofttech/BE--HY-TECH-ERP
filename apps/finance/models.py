import re
from datetime import date, timedelta

from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import Sum
from django.conf import settings


PERIOD_VALIDATOR = RegexValidator(
    regex=r'^Q[1-4]\s\d{4}$',
    message='Period must be in the format Q1 2026, Q2 2026, etc.',
)


def parse_period(period):
    """Return (start_date, end_date) for a period like 'Q1 2026' or None."""
    match = re.match(r'^Q([1-4])\s(\d{4})$', period)
    if not match:
        return None
    quarter, year = int(match.group(1)), int(match.group(2))
    start_month = (quarter - 1) * 3 + 1
    start = date(year, start_month, 1)
    if quarter == 4:
        end = date(year, 12, 31)
    else:
        end = date(year, start_month + 3, 1) - timedelta(days=1)
    return start, end


class BankAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('savings', 'Savings'),
        ('current', 'Current'),
    ]

    bank_name = models.CharField(max_length=255)
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, unique=True)
    ifsc_code = models.CharField(max_length=20)
    branch = models.CharField(max_length=255)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='savings')
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', 'bank_name']

    def __str__(self):
        return f'{self.bank_name} - {self.account_number}'


class ExpenseCategory(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Expense Categories'

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Expense(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    expense_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.CASCADE, related_name='expenses',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    date = models.DateField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.expense_id} - {self.name}'

    def save(self, *args, **kwargs):
        if not self.expense_id:
            self.expense_id = None
            super().save(*args, **kwargs)
            self.expense_id = f'EXP-{self.pk:04d}'
            super().save(update_fields=['expense_id'])
            return
        super().save(*args, **kwargs)


class Payment(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]

    payment_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    payee = models.CharField(max_length=200)
    bank = models.ForeignKey(
        BankAccount, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='payments',
    )
    payment_method = models.CharField(max_length=50, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.payment_id} - {self.payee}'

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = None
            super().save(*args, **kwargs)
            self.payment_id = f'PAY-{self.pk:04d}'
            super().save(update_fields=['payment_id'])
            return
        super().save(*args, **kwargs)


class Cashflow(models.Model):
    TYPE_CHOICES = [('inflow', 'Inflow'), ('outflow', 'Outflow')]
    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed')]

    ref_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    bank = models.ForeignKey(
        BankAccount, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='cashflows',
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    payment_method = models.CharField(max_length=50, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.ref_id} - {self.get_type_display()}'

    def save(self, *args, **kwargs):
        if not self.ref_id:
            self.ref_id = None
            super().save(*args, **kwargs)
            self.ref_id = f'CF-{self.pk:04d}'
            super().save(update_fields=['ref_id'])
            return
        super().save(*args, **kwargs)


class Budget(models.Model):
    budget_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    period = models.CharField(max_length=20, validators=[PERIOD_VALIDATOR])
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.CASCADE, related_name='budgets',
    )
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['period', 'category__name']

    def __str__(self):
        return f'{self.budget_id} - {self.period}'

    def save(self, *args, **kwargs):
        if not self.budget_id:
            self.budget_id = None
            super().save(*args, **kwargs)
            self.budget_id = f'BUD-{self.pk:04d}'
            super().save(update_fields=['budget_id'])
            return
        super().save(*args, **kwargs)

    def spent(self):
        period_range = parse_period(self.period)
        if not period_range:
            return 0
        start, end = period_range
        return self.category.expenses.filter(
            date__gte=start,
            date__lte=end,
            status__in=['paid', 'approved'],
        ).aggregate(total=Sum('amount'))['total'] or 0

    def remaining(self):
        return self.budget - self.spent()

    def usage_percent(self):
        total = self.budget
        if not total:
            return 0
        return round(float(self.spent()) / float(total) * 100, 2)


class Tax(models.Model):
    APPLIED_TO_CHOICES = [
        ('purchase', 'Purchase'),
        ('sales', 'Sales'),
        ('both', 'Both'),
    ]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    tax_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    applied_to = models.CharField(max_length=10, choices=APPLIED_TO_CHOICES, default='both')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.rate}%)'

    def save(self, *args, **kwargs):
        if not self.tax_id:
            self.tax_id = None
            super().save(*args, **kwargs)
            self.tax_id = f'TAX-{self.pk:04d}'
            super().save(update_fields=['tax_id'])
            return
        super().save(*args, **kwargs)


class IncomeCategory(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Income Categories'

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Income(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('partial', 'Partial'),
    ]

    income_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    party_name = models.CharField(
        max_length=200, help_text='Vendor or customer name.',
    )
    category = models.ForeignKey(
        IncomeCategory, on_delete=models.CASCADE, related_name='incomes',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.income_id} - {self.party_name}'

    def save(self, *args, **kwargs):
        if not self.income_id:
            self.income_id = None
            super().save(*args, **kwargs)
            self.income_id = f'INC-{self.pk:04d}'
            super().save(update_fields=['income_id'])
            return
        super().save(*args, **kwargs)


class PurchaseTax(models.Model):
    STATUS_CHOICES = [
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    bill_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    supplier = models.CharField(max_length=200)
    tax_type = models.ForeignKey(
        Tax, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='purchase_taxes',
    )
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Purchase Taxes'

    def __str__(self):
        return f'{self.bill_id} - {self.supplier}'

    def save(self, *args, **kwargs):
        if not self.bill_id:
            with transaction.atomic():
                last = PurchaseTax.objects.select_for_update().order_by('-id').first()
                self.bill_id = f'PT-{(last.id if last else 0) + 1:04d}'
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class Payroll(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    payroll_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payrolls',
        help_text='Employee this payroll belongs to.',
    )
    designation = models.ForeignKey(
        'settings_config.Designation',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payrolls',
    )
    department = models.ForeignKey(
        'settings_config.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payrolls',
    )
    payroll_month = models.CharField(
        max_length=7, help_text='Payroll month in YYYY-MM format.',
    )
    payment_date = models.DateField(null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    conveyance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pf = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Provident Fund deduction.',
    )
    professional_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tds = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earning = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Payrolls'

    def __str__(self):
        return f'{self.payroll_id or self.pk} - {self.employee} - {self.payroll_month}'

    def save(self, *args, **kwargs):
        self.total_earning = (
            self.basic_salary + self.hra + self.conveyance
            + self.bonus + self.other_allowance
        )
        self.total_deduction = (
            self.pf + self.professional_tax + self.tds + self.other_deductions
        )
        self.net_salary = self.total_earning - self.total_deduction
        if not self.payroll_id:
            self.payroll_id = None
            super().save(*args, **kwargs)
            self.payroll_id = f'PL-{self.pk:04d}'
            super().save(update_fields=['payroll_id'])
            return
        super().save(*args, **kwargs)
