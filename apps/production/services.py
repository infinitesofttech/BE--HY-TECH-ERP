from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.products.models import Inventory, Warehouse, adjust_inventory
from apps.purchases.models import Vendor, PurchaseOrder, PurchaseOrderItem
from apps.sales.models import DeliveryNote, DeliveryNoteItem

from .models import (
    Dispatch,
    FinishedGoods,
    GoodsReceiptNote,
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

def create_job_orders_from_sales_order(sales_order, start_date=None):
    """Create one JobOrder per product line of the approved sales order."""
    from apps.orders.models import Quotation
    from .models import Bom

    job_orders = []
    with transaction.atomic():
        for item in sales_order.items.select_related('product').all():
            bom = Bom.objects.filter(
                product=item.product, status='active',
            ).first()
            job_orders.append(JobOrder.objects.create(
                sales_order=sales_order,
                quotation=sales_order.quotation,
                customer=sales_order.customer,
                product=item.product,
                quantity=item.quantity,
                start_date=start_date or date.today(),
                bom=bom,
                status='planned',
            ))
    return job_orders


def refresh_material_requirement(requirement):
    """Recompute availability for a single material requirement."""
    available = Inventory.objects.filter(
        product=requirement.raw_material, status='active',
    ).aggregate(total=Sum('quantity'))['total'] or 0
    requirement.available_quantity = available
    if requirement.issued_quantity < requirement.required_quantity:
        requirement.status = (
            'available'
            if available >= requirement.required_quantity
            else 'short'
        )
    requirement.save(update_fields=['available_quantity', 'status', 'updated_at'])
    return requirement


def _finished_goods_available(product):
    """Available finished-goods stock for a BOM-less product.

    Uses the active inventory sum when warehouse records exist, falling back
    to the product quantity field otherwise.
    """
    total = Inventory.objects.filter(
        product=product, status='active',
    ).aggregate(total=Sum('quantity'))['total']
    if total is not None:
        return Decimal(total)
    quantity = (
        product.__class__.objects.filter(pk=product.pk)
        .values_list('quantity', flat=True).first() or 0
    )
    return Decimal(quantity)


def compute_material_requirements(job_order):
    """Derive material requirements from the BOM and compare with stock.

    Products without an active BOM are checked against their own stock
    (the product quantity) so shortages against the job quantity are still
    detected.
    """
    requirements = []
    if job_order.bom is None:
        if job_order.product is None:
            job_order.status = 'material_check'
            job_order.save(update_fields=['status', 'updated_at'])
            return requirements
        with transaction.atomic():
            required = Decimal(job_order.quantity)
            requirement, _ = MaterialRequirement.objects.update_or_create(
                job_order=job_order,
                raw_material=job_order.product,
                defaults={'required_quantity': required},
            )
            if requirement.issued_quantity > 0:
                requirement.status = 'issued'
            else:
                requirement.available_quantity = _finished_goods_available(
                    job_order.product,
                )
                requirement.status = (
                    'available'
                    if requirement.available_quantity >= required
                    else 'short'
                )
                requirement.save(
                    update_fields=['available_quantity', 'status', 'updated_at'],
                )
            requirements.append(requirement)
        job_order.status = (
            'material_ready'
            if requirement.status in ('available', 'issued')
            else 'waiting_material'
        )
        job_order.save(update_fields=['status', 'updated_at'])
        return requirements

    with transaction.atomic():
        for bom_item in job_order.bom.items.select_related('raw_material').all():
            required = Decimal(bom_item.quantity_per_unit) * job_order.quantity
            requirement, _ = MaterialRequirement.objects.update_or_create(
                job_order=job_order,
                raw_material=bom_item.raw_material,
                defaults={'required_quantity': required},
            )
            if requirement.issued_quantity > 0:
                requirement.status = 'issued'
            else:
                refresh_material_requirement(requirement)
            requirements.append(requirement)

    if requirements and all(
        r.status in ('available', 'issued') for r in requirements
    ):
        job_order.status = 'material_ready'
    else:
        job_order.status = 'waiting_material'
    job_order.save(update_fields=['status', 'updated_at'])
    return requirements


def check_stock(job_order):
    """API-friendly wrapper: recompute requirements and return status."""
    requirements = compute_material_requirements(job_order)
    return requirements


def issue_material(job_order, issued_to=None, created_by=None):
    """Issue all available raw materials for the job order.

    ``issued_to`` accepts a single value that is either an employee
    (User) id or a worker (Worker) id - the type is detected automatically.

    Decrements inventory and creates a MaterialIssueSlip. Raises ValueError
    if any material is short - create a PurchaseRequisition first.
    """
    requirements = list(job_order.material_requirements.all())
    if not requirements:
        requirements = compute_material_requirements(job_order)

    short = [r for r in requirements if r.status == 'short']
    if short:
        names = ', '.join(r.raw_material.name for r in short)
        raise ValueError(
            f'Insufficient stock for: {names}. '
            f'Create a purchase requisition first.'
        )

    issued_to, issued_to_worker = _resolve_issued_to(issued_to)

    with transaction.atomic():
        slip = MaterialIssueSlip.objects.create(
            job_order=job_order,
            issue_date=date.today(),
            issued_to=issued_to,
            issued_to_worker=issued_to_worker,
            created_by=created_by,
            status='issued',
        )
        items = []
        for requirement in requirements:
            quantity = requirement.required_quantity
            inventory_rows = list(Inventory.objects.select_for_update().filter(
                product=requirement.raw_material, status='active',
            ).order_by('-quantity'))
            total = sum(row.quantity for row in inventory_rows)
            if total < quantity:
                raise ValueError(
                    f'Insufficient stock for {requirement.raw_material.name}. '
                    f'Available: {total}, required: {quantity}.'
                )
            remaining = quantity
            for inventory in inventory_rows:
                if remaining <= 0:
                    break
                take = min(inventory.quantity, remaining)
                if take <= 0:
                    continue
                adjust_inventory(
                    requirement.raw_material, inventory.warehouse, -take,
                )
                items.append(MaterialIssueItem(
                    slip=slip,
                    raw_material=requirement.raw_material,
                    quantity=take,
                    warehouse=inventory.warehouse,
                ))
                remaining -= take
            if remaining > 0:
                raise ValueError(
                    f'Insufficient stock for {requirement.raw_material.name}. '
                    f'Available: {total}, required: {quantity}.'
                )
            requirement.issued_quantity = quantity
            requirement.status = 'issued'
            requirement.save(update_fields=['issued_quantity', 'status'])

        MaterialIssueItem.objects.bulk_create(items)
        job_order.status = 'material_issued'
        job_order.save(update_fields=['status', 'updated_at'])
    return slip


def create_purchase_requisition(job_order, requested_by=None, department='Production'):
    """Raise a purchase requisition for all short materials of the job order."""
    compute_material_requirements(job_order)
    short = job_order.material_requirements.filter(status='short')
    if not short.exists():
        raise ValueError('No material shortfall found. Nothing to requisition.')

    with transaction.atomic():
        requisition = PurchaseRequisition.objects.create(
            job_order=job_order,
            department=department,
            requested_by=requested_by,
            status='pending',
        )
        PurchaseRequisitionItem.objects.bulk_create([
            PurchaseRequisitionItem(
                requisition=requisition,
                raw_material=req.raw_material,
                quantity=req.required_quantity - req.available_quantity,
            )
            for req in short
        ])
        job_order.status = 'waiting_material'
        job_order.save(update_fields=['status', 'updated_at'])
    return requisition


def approve_purchase_requisition(requisition, approved_by=None):
    """Approve a requisition and auto-create a PurchaseOrder for its items."""
    if requisition.status not in ('pending', 'approved'):
        raise ValueError(
            f'Cannot approve a requisition in status "{requisition.status}".'
        )
    with transaction.atomic():
        requisition.approved_by = approved_by
        requisition.approval_date = date.today()
        requisition.status = 'approved'
        requisition.save()

        vendor = Vendor.objects.filter(status='active').first()
        if vendor is None:
            raise ValueError(
                'No active vendor available. Create a vendor first.'
            )

        purchase_order = PurchaseOrder.objects.create(
            vendor=vendor,
            reference=f'Requisition {requisition.requisition_no}',
            order_date=date.today(),
            status='pending',
        )
        item_objs = []
        for item in requisition.items.select_related('raw_material').all():
            unit_price = (
                item.raw_material.cost_price or item.raw_material.price
            )
            item_objs.append(PurchaseOrderItem(
                purchase_order=purchase_order,
                product=item.raw_material,
                quantity=item.quantity,
                unit_price=unit_price,
                amount=(item.quantity * unit_price),
            ))
        PurchaseOrderItem.objects.bulk_create(item_objs)
        purchase_order.recalculate_total()

        requisition.status = 'po_created'
        requisition.save(update_fields=['status'])
    return purchase_order


def reject_purchase_requisition(requisition, approved_by=None):
    """Reject a purchase requisition."""
    with transaction.atomic():
        requisition.approved_by = approved_by
        requisition.approval_date = date.today()
        requisition.status = 'rejected'
        requisition.save()
    return requisition


def create_grn(purchase_order, warehouse, received_by=None, received_date=None, notes=''):
    """Create a GRN for a purchase order (all items full quantity)."""
    grn = GoodsReceiptNote.objects.create(
        purchase_order=purchase_order,
        supplier=purchase_order.vendor,
        warehouse=warehouse,
        received_by=received_by,
        received_date=received_date or date.today(),
        status='received',
        notes=notes,
    )
    from .models import GRNItem

    GRNItem.objects.bulk_create([
        GRNItem(grn=grn, product=item.product, quantity=item.quantity)
        for item in purchase_order.items.all()
    ])
    return grn


def receive_grn(grn):
    """Update inventory with received goods and refresh material requirements."""
    if grn.warehouse is None:
        raise ValueError('A warehouse is required to receive goods.')
    with transaction.atomic():
        for item in grn.items.all():
            adjust_inventory(item.product, grn.warehouse, item.quantity)
            item.accepted_quantity = item.quantity
            item.save(update_fields=['accepted_quantity'])
        grn.status = 'received'
        grn.save(update_fields=['status', 'updated_at'])
        if grn.purchase_order is not None:
            order = grn.purchase_order
            order.status = 'received'
            order.actual_delivery_date = grn.received_date
            order.save(update_fields=['status', 'actual_delivery_date', 'updated_at'])
    _refresh_requirements_for_products([
        item.product_id for item in grn.items.all()
    ])
    return grn


def finalize_inspection(inspection, passed, inspected_by=None, notes=None):
    """Record a quality inspection result for purchase material (GRN)."""
    with transaction.atomic():
        inspection.status = 'passed' if passed else 'failed'
        inspection.inspected_by = inspected_by
        inspection.inspection_date = date.today()
        if notes is not None:
            inspection.notes = notes
        inspection.save()

        grn = inspection.grn
        if grn is not None:
            if passed:
                grn.status = 'accepted'
            else:
                grn.status = 'rejected'
                for item in grn.items.all():
                    adjust_inventory(
                        item.product, grn.warehouse, -item.quantity,
                    )
                    item.rejected_quantity = item.quantity
                    item.save(update_fields=['rejected_quantity'])
            grn.save(update_fields=['status', 'updated_at'])
    return inspection


def _resolve_fk(current, value, model):
    """Resolve a model instance or pk/id value to an instance.

    Falls back to the current value when the input is None or invalid so
    API views can pass raw primary keys without breaking.
    """
    if value is None or isinstance(value, model):
        return value
    if isinstance(value, bool):
        return None
    try:
        return model.objects.get(pk=value)
    except (model.DoesNotExist, TypeError, ValueError):
        return None


def _resolve_issued_to(value):
    """Resolve a single issued_to value to an (employee, worker) pair.

    The value is always a User id for both employees and workers (every
    worker is backed by a User), so no id collision is possible. A User
    that has a production worker profile maps to the worker column.
    """
    User = get_user_model()
    if value is None:
        return None, None
    if isinstance(value, Worker):
        return None, value
    if isinstance(value, User):
        user = value
    else:
        try:
            pk = int(value)
        except (TypeError, ValueError):
            raise ValueError(
                'Invalid issued_to. Must be a User id (employee or worker).'
            )
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise ValueError(
                'Invalid issued_to. No employee or worker found with that id.'
            )
    worker = getattr(user, 'production_worker_profile', None)
    if worker is not None:
        return None, worker
    return user, None


def start_production(job_order, machine=None, supervisor=None, operators=None,
                     process_names=None, workers=None):
    """Begin production: create the process checklist and start the first process.

    ``process_names`` must be existing active production stages (matched
    case-insensitively). They become the job-specific checklist in the given
    order. Raises ValueError when an unknown stage is supplied.
    """
    if isinstance(process_names, str):
        process_names = [process_names]
    if process_names:
        stages = {
            stage.name.lower(): stage.name
            for stage in ProductionStage.objects.filter(is_active=True)
        }
        missing = [
            name for name in process_names
            if not name or name.lower() not in stages
        ]
        if missing:
            raise ValueError(
                'Unknown production stage(s): {}. Choose from: {}.'.format(
                    ', '.join(missing),
                    ', '.join(sorted(set(stages.values()))),
                )
            )
        process_names = [stages[name.lower()] for name in process_names]
    with transaction.atomic():
        if not job_order.material_requirements.exists() and job_order.bom:
            compute_material_requirements(job_order)
        if process_names:
            job_order.processes.all().delete()
            for sequence, name in enumerate(process_names, start=1):
                ProductionProcess.objects.create(
                    job_order=job_order, sequence=sequence, name=name,
                )
        first = job_order.processes.order_by('sequence').first()
        if first and first.status == 'pending':
            first.status = 'in_progress'
            first.started_at = timezone.now()
            first.save()

        machine = _resolve_fk(job_order.machine, machine, Machine)
        supervisor = _resolve_fk(job_order.supervisor, supervisor, get_user_model())
        job_order.machine = machine if machine is not None else job_order.machine
        job_order.supervisor = supervisor if supervisor is not None else job_order.supervisor
        if operators is not None:
            job_order.operators.set(operators)
        if workers is not None:
            job_order.workers.set(workers)
        job_order.status = 'in_production'
        job_order.progress = 10
        job_order.save()
    return job_order


def advance_process(process):
    """Complete the current process and start the next one."""
    with transaction.atomic():
        process.status = 'completed'
        process.completed_at = timezone.now()
        process.save()

        job_order = process.job_order
        next_process = job_order.processes.filter(
            sequence__gt=process.sequence,
        ).order_by('sequence').first()
        total = job_order.processes.count()
        if next_process:
            next_process.status = 'in_progress'
            next_process.started_at = timezone.now()
            next_process.save()
            job_order.progress = min(
                95, round(next_process.sequence / total * 100),
            )
        else:
            job_order.progress = 95
        job_order.save()
    return process


def rework_process(job_order, notes=None):
    """Reset all processes before QC so production can run again."""
    with transaction.atomic():
        for process in job_order.processes.exclude(name__iexact='qc'):
            process.status = 'pending'
            process.started_at = None
            process.completed_at = None
            if notes is not None:
                process.notes = notes
            process.save()
        qc = job_order.processes.filter(name__iexact='qc').first()
        if qc:
            qc.status = 'pending'
            qc.started_at = None
            qc.completed_at = None
            qc.save()
        job_order.status = 'in_production'
        job_order.progress = 10
        job_order.save()
    return job_order


def record_qc_result(job_order, passed, inspected_by=None, notes=None, warehouse=None):
    """Record finished-goods QC. On pass creates FinishedGoods; on fail reopens work."""
    qc = job_order.processes.filter(name__iexact='qc').first()
    with transaction.atomic():
        if passed:
            batch_no = f'B{job_order.job_no}-{date.today():%Y%m%d}'
            warehouse = _resolve_fk(None, warehouse, Warehouse)
            finished = FinishedGoods.objects.create(
                job_order=job_order,
                product=job_order.product,
                quantity=job_order.quantity,
                batch_no=batch_no,
                warehouse=warehouse,
                status='in_stock',
            )
            if qc:
                qc.status = 'completed'
                qc.completed_at = timezone.now()
                qc.save()
            job_order.status = 'qc_passed'
            job_order.progress = 95
            job_order.save()
            return finished

        if qc:
            qc.status = 'rework'
            qc.save()
        job_order.status = 'qc_failed'
        job_order.progress = 50
        job_order.save()
        rework_process(job_order, notes=notes)
        return None


def create_dispatch(job_order, packing_note='', transport_mode='',
                    vehicle_number='', driver_name='', driver_phone='',
                    label_printed=True):
    """Package job output and auto-create a DeliveryNote for the customer."""
    finished = job_order.finished_goods.order_by('-created_at').first()
    if finished is None:
        raise ValueError('No finished goods available. Complete QC first.')

    customer = job_order.customer
    if customer is None:
        raise ValueError('Job order has no customer. Cannot create dispatch.')

    with transaction.atomic():
        dispatch = Dispatch.objects.create(
            job_order=job_order,
            sales_order=job_order.sales_order,
            customer=customer,
            packing_note=packing_note,
            transport_mode=transport_mode,
            vehicle_number=vehicle_number,
            driver_name=driver_name,
            driver_phone=driver_phone,
            label_printed=label_printed,
            status='packing',
        )

        unit_price = finished.product.price
        if job_order.sales_order_id:
            line = job_order.sales_order.items.filter(
                product=job_order.product,
            ).first()
            if line:
                unit_price = line.unit_price

        delivery_note = DeliveryNote.objects.create(
            customer=customer,
            reference=f'Job {job_order.job_no}',
            invoice_date=date.today(),
            status='active',
        )
        DeliveryNoteItem.objects.create(
            delivery_note=delivery_note,
            product=job_order.product,
            quantity=job_order.quantity,
            unit_price=unit_price,
            amount=unit_price * job_order.quantity,
        )
        delivery_note.recalculate_total()

        dispatch.delivery_note = delivery_note
        dispatch.status = 'ready'
        dispatch.save()

        finished.status = 'dispatched'
        finished.save()

        job_order.status = 'completed'
        job_order.progress = 100
        job_order.save()
        _complete_sales_order_if_done(job_order.sales_order)
    return dispatch


def mark_dispatch_dispatched(dispatch, vehicle_number='', driver_name='',
                             driver_phone=''):
    """Dispatch: capture transport details and move to delivered state."""
    with transaction.atomic():
        dispatch.status = 'dispatched'
        dispatch.dispatch_date = date.today()
        if vehicle_number:
            dispatch.vehicle_number = vehicle_number
        if driver_name:
            dispatch.driver_name = driver_name
        if driver_phone:
            dispatch.driver_phone = driver_phone
        dispatch.save()
    return dispatch


def _complete_sales_order_if_done(sales_order):
    if sales_order is None:
        return
    pending = sales_order.job_orders.exclude(
        status__in=['completed', 'cancelled'],
    ).exists()
    if not pending:
        sales_order.status = 'completed'
        sales_order.save(update_fields=['status', 'updated_at'])


def _refresh_requirements_for_products(product_ids):
    requirements = MaterialRequirement.objects.filter(
        raw_material_id__in=product_ids,
        status__in=['pending', 'short', 'available'],
    ).select_related('job_order')
    for requirement in requirements:
        refresh_material_requirement(requirement)
        job_order = requirement.job_order
        pending_short = job_order.material_requirements.filter(
            status='short',
        ).exists()
        if not pending_short:
            if job_order.status == 'waiting_material':
                job_order.status = 'material_ready'
                job_order.save(update_fields=['status', 'updated_at'])
