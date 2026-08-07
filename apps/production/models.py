from django.conf import settings
from django.db import models


class ProductionStage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sequence = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sequence']
        verbose_name = 'Production Stage'
        verbose_name_plural = 'Production Stages'

    def __str__(self):
        return f'{self.sequence}. {self.name}'


class Machine(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, blank=True)
    machine_type = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.code or self.id} - {self.name}'

    def save(self, *args, **kwargs):
        if not self.code:
            super().save(*args, **kwargs)
            self.code = f'M-{self.pk:03d}'
            super().save(update_fields=['code'])
            return
        super().save(*args, **kwargs)


class Bom(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=200)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='boms',
        help_text='Finished product this BOM is for.',
    )
    version = models.CharField(max_length=20, default='1.0')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product__name', '-created_at']

    def __str__(self):
        return f'{self.name} (v{self.version})'


class BomItem(models.Model):
    bom = models.ForeignKey(
        Bom,
        on_delete=models.CASCADE,
        related_name='items',
    )
    raw_material = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='bom_items',
        help_text='Raw material used in the product.',
    )
    quantity_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Quantity of raw material needed for one unit of finished product.',
    )
    unit = models.CharField(max_length=50, blank=True, default='piece')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.raw_material} x{self.quantity_per_unit} {self.unit}'


class JobOrder(models.Model):
    PRIORITY_CHOICES = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('material_check', 'Material Check'),
        ('material_ready', 'Material Ready'),
        ('waiting_material', 'Waiting for Material'),
        ('material_issued', 'Material Issued'),
        ('in_production', 'In Production'),
        ('qc_passed', 'QC Passed'),
        ('qc_failed', 'QC Failed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    job_no = models.CharField(max_length=20, unique=True, blank=True)
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_orders',
    )
    quotation = models.ForeignKey(
        'orders.Quotation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_orders',
    )
    customer = models.ForeignKey(
        'sales.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_orders',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='job_orders',
    )
    quantity = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    progress = models.PositiveIntegerField(
        default=0, help_text='Production progress percentage 0-100.',
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_orders',
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_job_orders',
    )
    operators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='job_order_operations',
    )
    bom = models.ForeignKey(
        Bom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_orders',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.job_no or f'JobOrder {self.pk}'

    def save(self, *args, **kwargs):
        if not self.job_no:
            super().save(*args, **kwargs)
            self.job_no = f'JO-{self.pk:04d}'
            super().save(update_fields=['job_no'])
            return
        super().save(*args, **kwargs)


class MaterialRequirement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('available', 'Available'),
        ('short', 'Short'),
        ('issued', 'Issued'),
    ]

    job_order = models.ForeignKey(
        JobOrder,
        on_delete=models.CASCADE,
        related_name='material_requirements',
    )
    raw_material = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='material_requirements',
    )
    required_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    available_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    issued_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        unique_together = [('job_order', 'raw_material')]

    def __str__(self):
        return f'{self.raw_material} for {self.job_order} ({self.status})'


class MaterialIssueSlip(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('issued', 'Issued'), ('closed', 'Closed')]

    slip_no = models.CharField(max_length=20, unique=True, blank=True)
    job_order = models.ForeignKey(
        JobOrder,
        on_delete=models.CASCADE,
        related_name='material_issue_slips',
    )
    issue_date = models.DateField()
    issued_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_material_slips',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_material_slips',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return self.slip_no or f'MaterialIssueSlip {self.pk}'

    def save(self, *args, **kwargs):
        if not self.slip_no:
            super().save(*args, **kwargs)
            self.slip_no = f'MIS-{self.pk:04d}'
            super().save(update_fields=['slip_no'])
            return
        super().save(*args, **kwargs)


class MaterialIssueItem(models.Model):
    slip = models.ForeignKey(
        MaterialIssueSlip,
        on_delete=models.CASCADE,
        related_name='items',
    )
    raw_material = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='material_issue_items',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    warehouse = models.ForeignKey(
        'products.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='material_issue_items',
    )

    def __str__(self):
        return f'{self.raw_material} x{self.quantity}'


class PurchaseRequisition(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('po_created', 'PO Created'),
        ('completed', 'Completed'),
    ]

    requisition_no = models.CharField(max_length=20, unique=True, blank=True)
    job_order = models.ForeignKey(
        JobOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_requisitions',
    )
    department = models.CharField(max_length=100, default='Production')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_requisitions',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_purchase_requisitions',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approval_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.requisition_no or f'PurchaseRequisition {self.pk}'

    def save(self, *args, **kwargs):
        if not self.requisition_no:
            super().save(*args, **kwargs)
            self.requisition_no = f'PRQ-{self.pk:04d}'
            super().save(update_fields=['requisition_no'])
            return
        super().save(*args, **kwargs)


class PurchaseRequisitionItem(models.Model):
    requisition = models.ForeignKey(
        PurchaseRequisition,
        on_delete=models.CASCADE,
        related_name='items',
    )
    raw_material = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='purchase_requisition_items',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    required_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.raw_material} x{self.quantity}'


class GoodsReceiptNote(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('inspected', 'Inspected'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    grn_no = models.CharField(max_length=20, unique=True, blank=True)
    purchase_order = models.ForeignKey(
        'purchases.PurchaseOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goods_receipt_notes',
    )
    supplier = models.ForeignKey(
        'purchases.Vendor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goods_receipt_notes',
    )
    warehouse = models.ForeignKey(
        'products.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goods_receipt_notes',
    )
    received_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='received')
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goods_receipts',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-received_date', '-created_at']

    def __str__(self):
        return self.grn_no or f'GRN {self.pk}'

    def save(self, *args, **kwargs):
        if not self.grn_no:
            super().save(*args, **kwargs)
            self.grn_no = f'GRN-{self.pk:04d}'
            super().save(update_fields=['grn_no'])
            return
        super().save(*args, **kwargs)


class GRNItem(models.Model):
    grn = models.ForeignKey(
        GoodsReceiptNote,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='grn_items',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    accepted_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rejected_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return f'{self.product} x{self.quantity}'


class QualityInspection(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('passed', 'Passed'), ('failed', 'Failed')]

    inspection_no = models.CharField(max_length=20, unique=True, blank=True)
    grn = models.ForeignKey(
        GoodsReceiptNote,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections',
        help_text='Purchase material inspection.',
    )
    job_order = models.ForeignKey(
        JobOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections',
        help_text='Finished goods inspection.',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quality_inspections',
    )
    inspection_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.inspection_no or f'Inspection {self.pk}'

    def save(self, *args, **kwargs):
        if not self.inspection_no:
            super().save(*args, **kwargs)
            self.inspection_no = f'QI-{self.pk:04d}'
            super().save(update_fields=['inspection_no'])
            return
        super().save(*args, **kwargs)


class ProductionProcess(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rework', 'Rework'),
        ('failed', 'Failed'),
    ]

    job_order = models.ForeignKey(
        JobOrder,
        on_delete=models.CASCADE,
        related_name='processes',
    )
    sequence = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['job_order', 'sequence']

    def __str__(self):
        return f'{self.job_order} - {self.name} ({self.status})'


class FinishedGoods(models.Model):
    STATUS_CHOICES = [('in_stock', 'In Stock'), ('dispatched', 'Dispatched')]

    finished_goods_no = models.CharField(max_length=20, unique=True, blank=True)
    job_order = models.ForeignKey(
        JobOrder,
        on_delete=models.CASCADE,
        related_name='finished_goods',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='finished_goods',
    )
    quantity = models.PositiveIntegerField()
    batch_no = models.CharField(max_length=100, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    warehouse = models.ForeignKey(
        'products.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='finished_goods',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='in_stock')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Finished Goods'

    def __str__(self):
        return f'{self.product} x{self.quantity} ({self.batch_no})'

    def save(self, *args, **kwargs):
        if not self.finished_goods_no:
            super().save(*args, **kwargs)
            self.finished_goods_no = f'FG-{self.pk:04d}'
            self.barcode = f'FG{self.pk:06d}'
            super().save(update_fields=['finished_goods_no', 'barcode'])
            return
        super().save(*args, **kwargs)


class Dispatch(models.Model):
    STATUS_CHOICES = [
        ('packing', 'Packing'),
        ('ready', 'Ready'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
    ]

    dispatch_no = models.CharField(max_length=20, unique=True, blank=True)
    job_order = models.ForeignKey(
        JobOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispatches',
    )
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispatches',
    )
    customer = models.ForeignKey(
        'sales.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispatches',
    )
    delivery_note = models.ForeignKey(
        'sales.DeliveryNote',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispatches',
    )
    packing_note = models.TextField(blank=True)
    label_printed = models.BooleanField(default=False)
    transport_mode = models.CharField(max_length=50, blank=True)
    vehicle_number = models.CharField(max_length=50, blank=True)
    driver_name = models.CharField(max_length=200, blank=True)
    driver_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='packing')
    dispatch_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.dispatch_no or f'Dispatch {self.pk}'

    def save(self, *args, **kwargs):
        if not self.dispatch_no:
            super().save(*args, **kwargs)
            self.dispatch_no = f'DS-{self.pk:04d}'
            super().save(update_fields=['dispatch_no'])
            return
        super().save(*args, **kwargs)
