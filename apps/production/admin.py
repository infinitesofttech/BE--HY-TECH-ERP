from django.contrib import admin

from .models import (
    Bom,
    BomItem,
    Dispatch,
    FinishedGoods,
    GoodsReceiptNote,
    GRNItem,
    JobOrder,
    Machine,
    MaterialIssueItem,
    MaterialIssueSlip,
    MaterialRequirement,
    ProductionProcess,
    ProductionStage,
    PurchaseRequisition,
    PurchaseRequisitionItem,
    QualityInspection,
)


@admin.register(ProductionStage)
class ProductionStageAdmin(admin.ModelAdmin):
    list_display = ['sequence', 'name', 'is_active']
    list_editable = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


class BomItemInline(admin.TabularInline):
    model = BomItem
    extra = 1


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'machine_type', 'status']
    list_filter = ['status', 'machine_type']
    search_fields = ['name', 'code']


@admin.register(Bom)
class BomAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'version', 'status']
    list_filter = ['status']
    search_fields = ['name', 'product__name']
    inlines = [BomItemInline]


class MaterialRequirementInline(admin.TabularInline):
    model = MaterialRequirement
    extra = 0
    readonly_fields = ['required_quantity', 'available_quantity', 'status']


class ProductionProcessInline(admin.TabularInline):
    model = ProductionProcess
    extra = 0
    readonly_fields = ['sequence', 'status']


@admin.register(JobOrder)
class JobOrderAdmin(admin.ModelAdmin):
    list_display = [
        'job_no', 'product', 'quantity', 'status', 'priority',
        'machine', 'start_date',
    ]
    list_filter = ['status', 'priority', 'machine']
    search_fields = ['job_no', 'product__name', 'customer__name']
    inlines = [MaterialRequirementInline, ProductionProcessInline]
    filter_horizontal = ['operators']


class MaterialIssueItemInline(admin.TabularInline):
    model = MaterialIssueItem
    extra = 0


@admin.register(MaterialIssueSlip)
class MaterialIssueSlipAdmin(admin.ModelAdmin):
    list_display = ['slip_no', 'job_order', 'issue_date', 'status']
    list_filter = ['status']
    search_fields = ['slip_no', 'job_order__job_no']
    inlines = [MaterialIssueItemInline]


class PurchaseRequisitionItemInline(admin.TabularInline):
    model = PurchaseRequisitionItem
    extra = 0


@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = [
        'requisition_no', 'job_order', 'department', 'status',
        'requested_by', 'approval_date',
    ]
    list_filter = ['status', 'department']
    search_fields = ['requisition_no', 'job_order__job_no']
    inlines = [PurchaseRequisitionItemInline]


class GRNItemInline(admin.TabularInline):
    model = GRNItem
    extra = 0


@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = [
        'grn_no', 'purchase_order', 'supplier', 'warehouse',
        'received_date', 'status',
    ]
    list_filter = ['status']
    search_fields = ['grn_no', 'supplier__name']
    inlines = [GRNItemInline]


@admin.register(QualityInspection)
class QualityInspectionAdmin(admin.ModelAdmin):
    list_display = [
        'inspection_no', 'grn', 'job_order', 'product', 'status',
        'inspected_by', 'inspection_date',
    ]
    list_filter = ['status']
    search_fields = ['inspection_no', 'grn__grn_no', 'job_order__job_no']


@admin.register(ProductionProcess)
class ProductionProcessAdmin(admin.ModelAdmin):
    list_display = ['job_order', 'sequence', 'name', 'status']
    list_filter = ['status', 'name']


@admin.register(FinishedGoods)
class FinishedGoodsAdmin(admin.ModelAdmin):
    list_display = [
        'finished_goods_no', 'job_order', 'product', 'quantity',
        'batch_no', 'barcode', 'status',
    ]
    list_filter = ['status']
    search_fields = ['finished_goods_no', 'batch_no', 'barcode', 'product__name']


@admin.register(Dispatch)
class DispatchAdmin(admin.ModelAdmin):
    list_display = [
        'dispatch_no', 'job_order', 'customer', 'status',
        'vehicle_number', 'driver_name', 'dispatch_date',
    ]
    list_filter = ['status']
    search_fields = ['dispatch_no', 'vehicle_number', 'driver_name']
