from rest_framework import serializers
import uuid
from django.db import transaction
from django.db.utils import IntegrityError

from .models import (
    Bom,
    BomItem,
    DailyWorkEntry,
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
    Worker,
)


class ProductionStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionStage
        fields = [
            'id', 'name', 'sequence', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


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
    worker_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductionProcess
        fields = [
            'id', 'sequence', 'name', 'worker', 'worker_name', 'status',
            'started_at', 'completed_at', 'notes',
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']

    def get_worker_name(self, obj):
        if obj.worker:
            return (obj.worker.worker_code
                    + ' - ' + (obj.worker.user.get_full_name()
                               or obj.worker.user.email
                               or ''))
        return ''


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
    product_name = serializers.CharField(source='product.name', read_only=True, default='')
    sales_order_id_ref = serializers.CharField(
        source='sales_order.order_id', read_only=True, default='',
    )
    customer_name = serializers.CharField(
        source='customer.name', read_only=True, default='',
    )
    supervisor_name = serializers.SerializerMethodField()
    machine_name = serializers.CharField(
        source='machine.name', read_only=True, default='',
    )
    bom_name = serializers.CharField(source='bom.name', read_only=True, default='')
    material_requirements = MaterialRequirementSerializer(many=True, read_only=True)
    processes = ProductionProcessSerializer(many=True, read_only=True)
    finished_goods = FinishedGoodsSerializer(many=True, read_only=True)
    workers_detail = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = JobOrder
        fields = [
            'id', 'job_no', 'sales_order', 'sales_order_id_ref', 'quotation',
            'customer', 'customer_name', 'product', 'product_name', 'quantity',
            'start_date', 'end_date', 'priority', 'status', 'status_display',
            'progress', 'machine', 'machine_name', 'supervisor', 'supervisor_name',
            'operators', 'workers', 'workers_detail', 'bom', 'bom_name', 'notes',
            'material_requirements', 'processes', 'finished_goods',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'job_no', 'progress', 'created_at', 'updated_at',
        ]

    def get_supervisor_name(self, obj):
        if obj.supervisor:
            return obj.supervisor.get_full_name() or obj.supervisor.email
        return ''

    def get_workers_detail(self, obj):
        return [
            {
                'id': w.id,
                'worker_id': w.user_id,
                'worker_code': w.worker_code,
                'name': w.user.get_full_name() or w.user.email,
                'worker_type': w.worker_type,
            }
            for w in obj.workers.all()
        ]


class JobOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOrder
        fields = [
            'id', 'sales_order', 'quotation', 'customer', 'product', 'quantity',
            'start_date', 'end_date', 'priority', 'machine', 'supervisor',
            'operators', 'workers', 'bom', 'notes',
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
    issued_to_worker_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    items = MaterialIssueItemSerializer(many=True, read_only=True)

    class Meta:
        model = MaterialIssueSlip
        fields = [
            'id', 'slip_no', 'job_order', 'job_no', 'issue_date', 'issued_to',
            'issued_to_name', 'issued_to_worker', 'issued_to_worker_name',
            'status', 'created_by', 'created_by_name',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slip_no', 'created_at', 'updated_at']

    def get_issued_to_name(self, obj):
        if obj.issued_to:
            return obj.issued_to.get_full_name() or obj.issued_to.email
        return ''

    def get_issued_to_worker_name(self, obj):
        if obj.issued_to_worker:
            return (obj.issued_to_worker.worker_code
                    + ' - ' + (obj.issued_to_worker.user.get_full_name()
                               or obj.issued_to_worker.user.email
                               or ''))
        return ''

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return ''


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
        return ''

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name() or obj.approved_by.email
        return ''


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
        return ''


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
        return ''


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


class WorkerSerializer(serializers.ModelSerializer):
    worker_id = serializers.SerializerMethodField()
    worker_name = serializers.CharField(source='user.get_full_name', read_only=True)
    worker_email = serializers.CharField(source='user.email', read_only=True)
    worker_phone = serializers.CharField(source='user.phone', read_only=True)
    machine_name = serializers.CharField(source='machine.name', read_only=True, default='')
    worker_type_display = serializers.CharField(source='get_worker_type_display', read_only=True)
    skill_level_display = serializers.CharField(source='get_skill_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    first_name = serializers.CharField(required=False, write_only=True, allow_blank=True)
    last_name = serializers.CharField(required=False, write_only=True, allow_blank=True)
    email = serializers.EmailField(required=False, write_only=True)
    phone = serializers.CharField(required=False, write_only=True, allow_blank=True)

    class Meta:
        model = Worker
        fields = [
            'id', 'worker_id', 'user', 'worker_code', 'worker_name',
            'worker_email', 'worker_phone', 'worker_type', 'worker_type_display',
            'skill_level', 'skill_level_display', 'machine', 'machine_name',
            'status', 'status_display', 'first_name', 'last_name', 'email',
            'phone', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'worker_code', 'created_at', 'updated_at']

    def get_worker_id(self, obj):
        return obj.user_id

    def update(self, instance, validated_data):
        user_fields = {
            'first_name': validated_data.pop('first_name', None),
            'last_name': validated_data.pop('last_name', None),
            'email': validated_data.pop('email', None),
            'phone': validated_data.pop('phone', None),
        }
        for field, value in user_fields.items():
            if value is not None:
                setattr(instance.user, field, value)
        if any(v is not None for v in user_fields.values()):
            instance.user.save()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class WorkerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False, write_only=True)
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True, allow_blank=True)
    email = serializers.EmailField(required=False, write_only=True)
    phone = serializers.CharField(required=False, write_only=True, allow_blank=True)
    password = serializers.CharField(required=False, write_only=True, min_length=8)

    class Meta:
        model = Worker
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'phone', 'password',
            'worker_type', 'skill_level', 'machine', 'status',
        ]

    def _create_user(self, attrs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        first_name = attrs.pop('first_name', '')
        last_name = attrs.pop('last_name', '')
        email = attrs.pop('email', None)
        phone = attrs.pop('phone', '')
        password = attrs.pop('password', None)

        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        if not email and not attrs.get('user_id'):
            raise serializers.ValidationError({'email': 'Either user_id or email is required.'})

        if attrs.get('user_id'):
            user = attrs.get('_user') or User.objects.get(pk=attrs['user_id'])
            if user.role != 'production_worker':
                user.role = 'production_worker'
                user.save(update_fields=['role'])
        else:
            username = email or f'worker_{uuid.uuid4().hex[:16]}'
            user = User(
                username=username,
                email=email or '',
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='production_worker',
            )
            if password:
                user.set_password(password)
            else:
                user.set_unusable_password()
            try:
                user.save()
            except IntegrityError:
                raise serializers.ValidationError(
                    {'email': 'A user with this email already exists.'}
                )
        return user

    def create(self, validated_data):
        user_fields = {
            'user_id': validated_data.pop('user_id', None),
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', ''),
            'email': validated_data.pop('email', None),
            'phone': validated_data.pop('phone', ''),
            'password': validated_data.pop('password', None),
        }
        with transaction.atomic():
            if user_fields.get('user_id'):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.select_for_update().get(pk=user_fields['user_id'])
                if Worker.objects.filter(user=user).exists():
                    raise serializers.ValidationError(
                        {'user_id': 'This user is already registered as a worker.'}
                    )
                user_fields['_user'] = user
            user = self._create_user(user_fields)
            worker = Worker.objects.create(user=user, **validated_data)
        return worker


class DailyWorkEntrySerializer(serializers.ModelSerializer):
    worker_name = serializers.SerializerMethodField()
    job_order_no = serializers.CharField(
        source='job_order.job_no', read_only=True, allow_null=True,
    )

    class Meta:
        model = DailyWorkEntry
        fields = [
            'id', 'worker', 'worker_name',
            'date', 'job_order', 'job_order_no',
            'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_worker_name(self, obj):
        return (
            obj.worker.user.get_full_name() or obj.worker.user.email
        )


class DailyWorkEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyWorkEntry
        fields = [
            'date', 'job_order', 'description',
        ]
        extra_kwargs = {
            'date': {'required': False},
            'description': {'required': False},
        }
