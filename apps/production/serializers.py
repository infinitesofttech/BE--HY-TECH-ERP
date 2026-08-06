from rest_framework import serializers

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
    PurchaseRequisition,
    PurchaseRequisitionItem,
    QualityInspection,
)


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = [
            'id', 'name', 'code', 'machine_type', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class BomItemSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.CharField(
        source='raw_material.name', read_only=True,
    )

    class Meta:
        model = BomItem
        fields = [
            'id', 'raw_material', 'raw_material_name',
            'quantity_per_unit', 'unit',
        ]
        read_only_fields = ['id']


class BomSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    items = BomItemSerializer(many=True, read_only=True)

    class Meta:
        model = Bom
        fields = [
            'id', 'name', 'product', 'product_name', 'version',
            'status', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BomItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BomItem
        fields = ['raw_material', 'quantity_per_unit', 'unit']


class BomCreateSerializer(serializers.ModelSerializer):
    items = BomItemCreateSerializer(many=True, required=False)

    class Meta:
        model = Bom
        fields = ['id', 'name', 'product', 'version', 'status', 'items']
        read_only_fields = ['id']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bom = Bom.objects.create(**validated_data)
        BomItem.objects.bulk_create([
            BomItem(bom=bom, **item_data) for item_data in items_data
        ])
        return bom


class MaterialRequirementSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.CharField(
        source='raw_material.name', read_only=True,
    )

    class Meta:
        model = MaterialRequirement
        fields = [
            'id', 'raw_material', 'raw_material_name', 'required_quantity',
            'available_quantity', 'issued_quantity', 'status', 'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


class ProductionProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionProcess
        fields = [
            'id', 'sequence', 'name', 'status', 'started_at',
            'completed_at', 'notes',
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']


class FinishedGoodsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    job_no = serializers.CharField(source='job_order.job_no', read_only=True)

    class Meta:
        model = FinishedGoods
        fields = [
            'id', 'finished_goods_no', 'job_order', 'job_no', 'product',
            'product_name', 'quantity', 'batch_no', 'barcode', 'warehouse',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'finished_goods_no', 'barcode', 'created_at', 'updated_at']


class JobOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    sales_order_id_ref = serializers.CharField(
        source='sales_order.order_id', read_only=True,
    )
    customer_name = serializers.CharField(
        source='customer.name', read_only=True,
    )
    supervisor_name = serializers.SerializerMethodField()
    machine_name = serializers.CharField(
        source='machine.name', read_only=True, default='',
    )
    bom_name = serializers.CharField(source='bom.name', read_only=True, default='')
    material_requirements = MaterialRequirementSerializer(many=True, read_only=True)
    processes = ProductionProcessSerializer(many=True, read_only=True)
    finished_goods = FinishedGoodsSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = JobOrder
        fields = [
            'id', 'job_no', 'sales_order', 'sales_order_id_ref', 'quotation',
            'customer', 'customer_name', 'product', 'product_name', 'quantity',
            'start_date', 'end_date', 'priority', 'status', 'status_display',
            'progress', 'machine', 'machine_name', 'supervisor', 'supervisor_name',
            'operators', 'bom', 'bom_name', 'notes', 'material_requirements',
            'processes', 'finished_goods', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'job_no', 'progress', 'created_at', 'updated_at',
        ]

    def get_supervisor_name(self, obj):
        if obj.supervisor:
            return obj.supervisor.get_full_name() or obj.supervisor.email
        return None


class JobOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOrder
        fields = [
            'id', 'sales_order', 'quotation', 'customer', 'product', 'quantity',
            'start_date', 'end_date', 'priority', 'machine', 'supervisor',
            'operators', 'bom', 'notes',
        ]
        read_only_fields = ['id']


class MaterialIssueItemSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.CharField(
        source='raw_material.name', read_only=True,
    )
    warehouse_name = serializers.CharField(
        source='warehouse.name', read_only=True, default='',
    )

    class Meta:
        model = MaterialIssueItem
        fields = [
            'id', 'raw_material', 'raw_material_name', 'quantity', 'warehouse',
            'warehouse_name',
        ]
        read_only_fields = ['id']


class MaterialIssueSlipSerializer(serializers.ModelSerializer):
    job_no = serializers.CharField(source='job_order.job_no', read_only=True)
    issued_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    items = MaterialIssueItemSerializer(many=True, read_only=True)

    class Meta:
        model = MaterialIssueSlip
        fields = [
            'id', 'slip_no', 'job_order', 'job_no', 'issue_date', 'issued_to',
            'issued_to_name', 'status', 'created_by', 'created_by_name',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slip_no', 'created_at', 'updated_at']

    def get_issued_to_name(self, obj):
        if obj.issued_to:
            return obj.issued_to.get_full_name() or obj.issued_to.email
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class PurchaseRequisitionItemSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.CharField(
        source='raw_material.name', read_only=True,
    )

    class Meta:
        model = PurchaseRequisitionItem
        fields = [
            'id', 'raw_material', 'raw_material_name', 'quantity',
            'required_date',
        ]
        read_only_fields = ['id']


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    job_no = serializers.CharField(source='job_order.job_no', read_only=True, default='')
    requested_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    items = PurchaseRequisitionItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = [
            'id', 'requisition_no', 'job_order', 'job_no', 'department',
            'requested_by', 'requested_by_name', 'approved_by',
            'approved_by_name', 'status', 'status_display', 'approval_date',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'requisition_no', 'approval_date', 'created_at', 'updated_at',
        ]

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return obj.requested_by.get_full_name() or obj.requested_by.email
        return None

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name() or obj.approved_by.email
        return None


class GRNItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = GRNItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'accepted_quantity',
            'rejected_quantity', 'rejection_reason',
        ]
        read_only_fields = ['id', 'accepted_quantity', 'rejected_quantity']


class GoodsReceiptNoteSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True, default='')
    purchase_order_id_ref = serializers.CharField(
        source='purchase_order.purchase_order_id', read_only=True, default='',
    )
    warehouse_name = serializers.CharField(
        source='warehouse.name', read_only=True, default='',
    )
    received_by_name = serializers.SerializerMethodField()
    items = GRNItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = GoodsReceiptNote
        fields = [
            'id', 'grn_no', 'purchase_order', 'purchase_order_id_ref',
            'supplier', 'supplier_name', 'warehouse', 'warehouse_name',
            'received_date', 'status', 'status_display', 'received_by',
            'received_by_name', 'notes', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'grn_no', 'created_at', 'updated_at',
        ]

    def get_received_by_name(self, obj):
        if obj.received_by:
            return obj.received_by.get_full_name() or obj.received_by.email
        return None


class GRNItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRNItem
        fields = ['product', 'quantity', 'rejection_reason']


class GoodsReceiptNoteCreateSerializer(serializers.ModelSerializer):
    items = GRNItemCreateSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptNote
        fields = [
            'id', 'purchase_order', 'supplier', 'warehouse', 'received_date',
            'status', 'received_by', 'notes', 'items',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        grn = GoodsReceiptNote.objects.create(**validated_data)
        GRNItem.objects.bulk_create([
            GRNItem(grn=grn, **item_data) for item_data in items_data
        ])
        return grn


class QualityInspectionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default='')
    grn_no = serializers.CharField(source='grn.grn_no', read_only=True, default='')
    job_no = serializers.CharField(source='job_order.job_no', read_only=True, default='')
    inspected_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = QualityInspection
        fields = [
            'id', 'inspection_no', 'grn', 'grn_no', 'job_order', 'job_no',
            'product', 'product_name', 'quantity', 'status', 'status_display',
            'inspected_by', 'inspected_by_name', 'inspection_date', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'inspection_no', 'inspection_date', 'created_at', 'updated_at']

    def get_inspected_by_name(self, obj):
        if obj.inspected_by:
            return obj.inspected_by.get_full_name() or obj.inspected_by.email
        return None


class DispatchSerializer(serializers.ModelSerializer):
    job_no = serializers.CharField(source='job_order.job_no', read_only=True, default='')
    sales_order_id_ref = serializers.CharField(
        source='sales_order.order_id', read_only=True, default='',
    )
    customer_name = serializers.CharField(source='customer.name', read_only=True, default='')
    delivery_note_id_ref = serializers.CharField(
        source='delivery_note.delivery_note_id', read_only=True, default='',
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Dispatch
        fields = [
            'id', 'dispatch_no', 'job_order', 'job_no', 'sales_order',
            'sales_order_id_ref', 'customer', 'customer_name',
            'delivery_note', 'delivery_note_id_ref', 'packing_note',
            'label_printed', 'transport_mode', 'vehicle_number', 'driver_name',
            'driver_phone', 'status', 'status_display', 'dispatch_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'dispatch_no', 'created_at', 'updated_at']


class DispatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispatch
        fields = [
            'job_order', 'packing_note', 'label_printed', 'transport_mode',
            'vehicle_number', 'driver_name', 'driver_phone',
        ]
        read_only_fields = ['id']
