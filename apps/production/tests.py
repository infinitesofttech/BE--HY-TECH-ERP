from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.finance.models import Tax
from apps.invoices.models import Invoice
from apps.invoices.services import create_invoice_from_delivery_note, mark_invoice_paid
from apps.orders.models import Quotation, QuotationItem
from apps.orders.serializers import QuotationCreateSerializer
from apps.orders.services import approve_quotation, send_quotation
from apps.pipeline.models import Lead
from apps.production import services as production_services
from apps.production.models import (
    Bom,
    BomItem,
    FinishedGoods,
    GoodsReceiptNote,
    GRNItem,
    JobOrder,
    Machine,
    MaterialIssueSlip,
    MaterialRequirement,
    ProductionProcess,
    PurchaseRequisition,
    QualityInspection,
)
from apps.products.models import Inventory, Product, ProductCategory, Warehouse
from apps.purchases.models import PurchaseOrder, Vendor
from apps.sales.models import Customer, DeliveryNote, SalesOrder, SalesOrderItem


class ProductionWorkflowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='admin',
            email='admin@production.test',
            password='testpass123',
            role='super_admin',
        )
        category = ProductCategory.objects.create(name='Steel Products')

        self.steel_sheet = Product.objects.create(
            name='Steel Sheet', category=category,
            cost_price=100, price=120, unit='sheet',
        )
        self.pipe = Product.objects.create(
            name='Pipe', category=category,
            cost_price=40, price=50, unit='meter',
        )
        self.cabinet = Product.objects.create(
            name='Steel Cabinet', category=category,
            cost_price=500, price=800, unit='piece',
        )
        self.tax = Tax.objects.create(
            name='GST 18%', rate=18, status='active', applied_to='both',
        )
        self.warehouse = Warehouse.objects.create(name='Main Store')
        Inventory.objects.create(
            product=self.steel_sheet, warehouse=self.warehouse, quantity=50,
        )
        Inventory.objects.create(
            product=self.pipe, warehouse=self.warehouse, quantity=30,
        )
        self.vendor = Vendor.objects.create(
            name='Raw Supplier', email='supplier@example.com',
        )
        self.customer = Customer.objects.create(
            name='Acme Corp', email='acme@example.com', phone='9876543210',
        )
        self.machine = Machine.objects.create(name='CNC Cutting Machine')

        self.bom = Bom.objects.create(
            name='Cabinet BOM', product=self.cabinet, version='1.0',
        )
        BomItem.objects.create(
            bom=self.bom, raw_material=self.steel_sheet,
            quantity_per_unit=4, unit='sheet',
        )
        BomItem.objects.create(
            bom=self.bom, raw_material=self.pipe,
            quantity_per_unit=2, unit='meter',
        )

    def _create_quotation(self):
        lead = Lead.objects.create(
            first_name='John', last_name='Doe',
            company_name='Acme Corp', email='acme@example.com',
            phone='9876543210', product_requirement='Steel Cabinet',
            quantity=2, status='new', owner=self.user,
        )
        quotation = Quotation.objects.create(
            client='Acme Corp',
            lead=lead,
            customer=self.customer,
            quote_date=date(2026, 8, 1),
            valid_till=date(2026, 8, 15),
            delivery_date=date(2026, 8, 25),
            payment_terms='net_30',
            tax=self.tax,
            status='draft',
            created_by=self.user,
        )
        QuotationItem.objects.create(
            quotation=quotation, product=self.cabinet,
            quantity=2, price=800, discount=0,
        )
        quotation.recalculate_totals()
        return lead, quotation

    def test_lead_to_quotation_to_sales_order(self):
        lead, quotation = self._create_quotation()
        send_quotation(quotation)
        self.assertEqual(quotation.status, 'sent')

        sales_order = approve_quotation(quotation, employee=self.user)
        quotation.refresh_from_db()
        lead.refresh_from_db()
        self.assertEqual(quotation.status, 'accepted')
        self.assertEqual(lead.status, 'won')
        self.assertIsInstance(sales_order, SalesOrder)
        self.assertEqual(sales_order.quotation, quotation)
        self.assertEqual(sales_order.customer, self.customer)
        self.assertEqual(sales_order.items.count(), 1)
        self.assertGreater(sales_order.total_amount, 0)

    def test_sales_order_to_job_orders(self):
        _, quotation = self._create_quotation()
        sales_order = approve_quotation(quotation, employee=self.user)
        job_orders = production_services.create_job_orders_from_sales_order(
            sales_order,
        )
        self.assertEqual(len(job_orders), 1)
        job_order = job_orders[0]
        self.assertEqual(job_order.product, self.cabinet)
        self.assertEqual(job_order.quantity, 2)
        self.assertEqual(job_order.bom, self.bom)
        self.assertTrue(job_order.job_no.startswith('JO-'))

    def test_stock_check_and_material_issue(self):
        job_order = JobOrder.objects.create(
            sales_order=None,
            customer=self.customer,
            product=self.cabinet,
            quantity=2,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        requirements = production_services.compute_material_requirements(
            job_order,
        )
        self.assertEqual(len(requirements), 2)
        job_order.refresh_from_db()
        self.assertEqual(job_order.status, 'material_ready')

        slip = production_services.issue_material(
            job_order, created_by=self.user,
        )
        self.assertIsInstance(slip, MaterialIssueSlip)
        self.assertEqual(slip.items.count(), 2)
        job_order.refresh_from_db()
        self.assertEqual(job_order.status, 'material_issued')
        self.steel_sheet.refresh_from_db()
        self.pipe.refresh_from_db()
        self.assertEqual(
            Inventory.objects.get(product=self.steel_sheet).quantity, 42,
        )
        self.assertEqual(
            Inventory.objects.get(product=self.pipe).quantity, 26,
        )

    def test_product_without_bom_checks_own_stock_and_creates_requisition(self):
        Product.objects.filter(pk=self.cabinet.pk).update(quantity=26)
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=40,
            start_date=date(2026, 8, 10),
        )
        requirements = production_services.compute_material_requirements(
            job_order,
        )
        self.assertEqual(len(requirements), 1)
        requirement = requirements[0]
        self.assertEqual(requirement.raw_material, self.cabinet)
        self.assertEqual(requirement.required_quantity, Decimal('40'))
        self.assertEqual(requirement.available_quantity, Decimal('26'))
        self.assertEqual(requirement.status, 'short')
        job_order.refresh_from_db()
        self.assertEqual(job_order.status, 'waiting_material')

        requisition = production_services.create_purchase_requisition(
            job_order, requested_by=self.user,
        )
        self.assertIsInstance(requisition, PurchaseRequisition)
        self.assertEqual(requisition.items.count(), 1)
        item = requisition.items.first()
        self.assertEqual(item.raw_material, self.cabinet)
        self.assertEqual(item.quantity, Decimal('14'))

    def test_product_without_bom_marked_available_when_stock_sufficient(self):
        Product.objects.filter(pk=self.cabinet.pk).update(quantity=26)
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=20,
            start_date=date(2026, 8, 10),
        )
        requirements = production_services.compute_material_requirements(
            job_order,
        )
        self.assertEqual(requirements[0].status, 'available')
        job_order.refresh_from_db()
        self.assertEqual(job_order.status, 'material_ready')

    def test_issue_material_uses_stock_across_multiple_warehouses(self):
        second = Warehouse.objects.create(name='Second Warehouse')
        Inventory.objects.create(
            product=self.cabinet, warehouse=self.warehouse, quantity=15,
        )
        Inventory.objects.create(
            product=self.cabinet, warehouse=second, quantity=25,
        )
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=40,
            start_date=date(2026, 8, 10),
        )
        slip = production_services.issue_material(
            job_order, created_by=self.user,
        )
        slip.refresh_from_db()
        self.assertEqual(slip.items.count(), 2)
        quantities = {item.quantity for item in slip.items.all()}
        self.assertEqual(quantities, {15, 25})
        self.assertEqual(
            Inventory.objects.get(
                product=self.cabinet, warehouse=self.warehouse,
            ).quantity, 0,
        )
        self.assertEqual(
            Inventory.objects.get(
                product=self.cabinet, warehouse=second,
            ).quantity, 0,
        )

    def test_short_material_creates_requisition_and_po(self):
        Inventory.objects.filter(product=self.steel_sheet).update(quantity=2)
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=2,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        production_services.compute_material_requirements(job_order)
        job_order.refresh_from_db()
        self.assertEqual(job_order.status, 'waiting_material')

        requisition = production_services.create_purchase_requisition(
            job_order, requested_by=self.user,
        )
        self.assertIsInstance(requisition, PurchaseRequisition)
        self.assertEqual(requisition.status, 'pending')
        self.assertEqual(requisition.items.count(), 1)
        self.assertEqual(
            requisition.items.first().raw_material, self.steel_sheet,
        )

        purchase_order = production_services.approve_purchase_requisition(
            requisition, approved_by=self.user,
        )
        requisition.refresh_from_db()
        self.assertEqual(requisition.status, 'po_created')
        self.assertIsInstance(purchase_order, PurchaseOrder)

        grn = production_services.create_grn(
            purchase_order, self.warehouse, received_by=self.user,
        )
        self.assertIsInstance(grn, GoodsReceiptNote)
        grn = production_services.receive_grn(grn)
        grn.refresh_from_db()
        self.assertEqual(grn.status, 'received')

        inspection = QualityInspection.objects.create(grn=grn, status='pending')
        production_services.finalize_inspection(
            inspection, passed=True, inspected_by=self.user,
        )
        inspection.refresh_from_db()
        grn.refresh_from_db()
        self.assertEqual(inspection.status, 'passed')
        self.assertEqual(grn.status, 'accepted')

        self.steel_sheet.refresh_from_db()
        self.assertEqual(
            Inventory.objects.get(product=self.steel_sheet).quantity, 8,
        )

    def test_lead_requirement_quantity_is_used_for_quotation_sales_order_and_materials(self):
        lead = Lead.objects.create(
            first_name='Jane', last_name='Buyer', company_name='Acme Corp',
            email='jane@example.com', phone='9999999999',
            product_requirement='Steel Cabinet', quantity=3, status='new',
            owner=self.user,
        )
        serializer = QuotationCreateSerializer(data={
            'client': 'Acme Corp',
            'lead': lead.id,
            'quote_date': '2026-08-01',
            'valid_till': '2026-08-15',
            'delivery_date': '2026-08-25',
            'payment_terms': 'net_30',
            'tax': self.tax.id,
            'status': 'draft',
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        quotation = serializer.save(created_by=self.user)

        sales_order = approve_quotation(quotation, employee=self.user)
        job_orders = production_services.create_job_orders_from_sales_order(sales_order)
        self.assertEqual(job_orders[0].quantity, lead.quantity)

        requirements = production_services.compute_material_requirements(job_orders[0])
        self.assertEqual(len(requirements), 2)
        steel_requirement = next(r for r in requirements if r.raw_material == self.steel_sheet)
        pipe_requirement = next(r for r in requirements if r.raw_material == self.pipe)
        self.assertEqual(steel_requirement.required_quantity, Decimal('12'))
        self.assertEqual(pipe_requirement.required_quantity, Decimal('6'))

        Inventory.objects.filter(product=self.steel_sheet).update(quantity=2)
        Inventory.objects.filter(product=self.pipe).update(quantity=5)
        production_services.compute_material_requirements(job_orders[0])
        job_orders[0].refresh_from_db()
        self.assertEqual(job_orders[0].status, 'waiting_material')

        requisition = production_services.create_purchase_requisition(
            job_orders[0], requested_by=self.user,
        )
        self.assertEqual(requisition.items.count(), 2)

    def test_production_process_and_qc(self):
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=1,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        production_services.issue_material(job_order, created_by=self.user)
        job_order = production_services.start_production(
            job_order, machine=self.machine, supervisor=self.user,
            process_names=[
                'cutting', 'fabrication', 'machining', 'welding',
                'grinding', 'painting', 'assembly', 'qc',
            ],
        )
        self.assertEqual(job_order.status, 'in_production')
        self.assertEqual(job_order.processes.count(), 8)

        for process in job_order.processes.exclude(name__iexact='qc'):
            production_services.advance_process(process)

        finished = production_services.record_qc_result(
            job_order, passed=True, inspected_by=self.user,
            warehouse=self.warehouse,
        )
        job_order.refresh_from_db()
        self.assertIsInstance(finished, FinishedGoods)
        self.assertEqual(job_order.status, 'qc_passed')
        self.assertTrue(finished.batch_no)
        self.assertTrue(finished.barcode)

    def test_start_production_accepts_machine_and_supervisor_pk(self):
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=1,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        production_services.issue_material(job_order, created_by=self.user)
        job_order = production_services.start_production(
            job_order, machine=self.machine.id, supervisor=self.user.id,
        )
        job_order.refresh_from_db()
        self.assertEqual(job_order.machine, self.machine)
        self.assertEqual(job_order.supervisor, self.user)

    def test_start_production_accepts_custom_process_names(self):
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=1,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        production_services.issue_material(job_order, created_by=self.user)
        custom_stages = ['Cutting', 'Fabrication', 'Welding', 'Painting', 'QC']
        job_order = production_services.start_production(
            job_order, process_names=custom_stages,
        )
        processes = list(job_order.processes.order_by('sequence'))
        self.assertEqual(
            [p.name for p in processes],
            ['cutting', 'fabrication', 'welding', 'painting', 'qc'],
        )
        self.assertEqual(
            [p.sequence for p in processes], [1, 2, 3, 4, 5],
        )
        self.assertEqual(processes[0].status, 'in_progress')
        self.assertEqual(job_order.status, 'in_production')

    def test_start_production_replaces_existing_processes(self):
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=1,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        production_services.issue_material(job_order, created_by=self.user)
        production_services.start_production(
            job_order, process_names=['cutting', 'welding', 'qc'],
        )
        production_services.start_production(
            job_order, process_names=['Cutting', 'Welding', 'Painting', 'QC'],
        )
        processes = list(job_order.processes.order_by('sequence'))
        self.assertEqual(
            [p.name for p in processes],
            ['cutting', 'welding', 'painting', 'qc'],
        )
        self.assertEqual(len(processes), 4)

    def test_start_production_rejects_unknown_stage(self):
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=1,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        production_services.issue_material(job_order, created_by=self.user)
        with self.assertRaises(ValueError):
            production_services.start_production(
                job_order, process_names=['Cutting', 'Bending', 'QC'],
            )
        self.assertEqual(job_order.processes.count(), 0)
        self.assertEqual(job_order.status, 'material_issued')

    def test_record_qc_result_accepts_warehouse_pk(self):
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=1,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        production_services.issue_material(job_order, created_by=self.user)
        finished = production_services.record_qc_result(
            job_order, passed=True, inspected_by=self.user,
            warehouse=self.warehouse.id,
        )
        job_order.refresh_from_db()
        self.assertIsInstance(finished, FinishedGoods)
        self.assertEqual(finished.warehouse, self.warehouse)
        self.assertEqual(job_order.status, 'qc_passed')

    def test_issue_material_accepts_issued_to_pk(self):
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=1,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        slip = production_services.issue_material(
            job_order, issued_to=self.user.id, created_by=self.user,
        )
        slip.refresh_from_db()
        self.assertEqual(slip.issued_to, self.user)

    def test_qc_failure_opens_rework(self):
        job_order = JobOrder.objects.create(
            customer=self.customer,
            product=self.cabinet,
            quantity=1,
            start_date=date(2026, 8, 10),
            bom=self.bom,
        )
        production_services.issue_material(job_order, created_by=self.user)
        production_services.start_production(
            job_order,
            process_names=[
                'cutting', 'fabrication', 'machining', 'welding',
                'grinding', 'painting', 'assembly', 'qc',
            ],
        )
        result = production_services.record_qc_result(
            job_order, passed=False, inspected_by=self.user,
        )
        job_order.refresh_from_db()
        self.assertIsNone(result)
        self.assertEqual(job_order.status, 'in_production')
        self.assertEqual(
            job_order.processes.exclude(name__iexact='qc')
            .filter(status='pending').count(), 7,
        )

    def test_dispatch_creates_delivery_note_and_completes_order(self):
        _, quotation = self._create_quotation()
        sales_order = approve_quotation(quotation, employee=self.user)
        job_order = production_services.create_job_orders_from_sales_order(
            sales_order,
        )[0]
        production_services.issue_material(job_order, created_by=self.user)
        production_services.start_production(
            job_order,
            process_names=[
                'cutting', 'fabrication', 'machining', 'welding',
                'grinding', 'painting', 'assembly', 'qc',
            ],
        )
        for process in job_order.processes.exclude(name__iexact='qc'):
            production_services.advance_process(process)
        production_services.record_qc_result(
            job_order, passed=True, inspected_by=self.user,
            warehouse=self.warehouse,
        )

        dispatch = production_services.create_dispatch(
            job_order, transport_mode='Truck', vehicle_number='KA-01-1234',
            driver_name='Ramesh', driver_phone='9000000000',
        )
        job_order.refresh_from_db()
        sales_order.refresh_from_db()
        self.assertEqual(dispatch.delivery_note.delivery_note_id[:2], 'DN')
        self.assertEqual(dispatch.delivery_note.customer, self.customer)
        self.assertEqual(job_order.status, 'completed')
        self.assertEqual(sales_order.status, 'completed')
        self.assertEqual(
            job_order.finished_goods.first().status, 'dispatched',
        )

        invoice = create_invoice_from_delivery_note(dispatch.delivery_note)
        self.assertIsInstance(invoice, Invoice)
        self.assertTrue(invoice.invoice_number.startswith('INV-'))
        self.assertEqual(invoice.customer_name, 'Acme Corp')
        self.assertGreater(invoice.total, 0)

        mark_invoice_paid(invoice, method='bank_transfer')
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'paid')
        self.assertEqual(invoice.payments.count(), 1)


class ProductionAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='admin', email='admin@production.test',
            password='testpass123', role='super_admin',
        )
        self.client = APIClient()
        category = ProductCategory.objects.create(name='Steel Products')
        self.product = Product.objects.create(
            name='Steel Cabinet', category=category, price=800,
        )
        self.raw = Product.objects.create(
            name='Steel Sheet', category=category, cost_price=100, price=120,
        )
        self.warehouse = Warehouse.objects.create(name='Main Store')
        Inventory.objects.create(
            product=self.raw, warehouse=self.warehouse, quantity=10,
        )
        self.customer = Customer.objects.create(name='Acme Corp')
        self.bom = Bom.objects.create(name='Cabinet BOM', product=self.product)
        BomItem.objects.create(
            bom=self.bom, raw_material=self.raw, quantity_per_unit=1,
        )
        self.client.force_authenticate(user=self.admin)

    def test_quotation_approve_creates_sales_order(self):
        quotation = Quotation.objects.create(
            client='Acme Corp', customer=self.customer, status='sent',
            created_by=self.admin,
        )
        QuotationItem.objects.create(
            quotation=quotation, product=self.product,
            quantity=1, price=800,
        )
        quotation.recalculate_totals()
        response = self.client.post(
            f'/api/orders/quotations/{quotation.id}/approve/',
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('sales_order', response.data)
        self.assertEqual(
            SalesOrder.objects.filter(quotation=quotation).count(), 1,
        )

    def test_quotation_reject_marks_lead_lost(self):
        lead = Lead.objects.create(first_name='John', last_name='Doe')
        quotation = Quotation.objects.create(
            client='Acme Corp', lead=lead, status='sent',
            created_by=self.admin,
        )
        response = self.client.post(
            f'/api/orders/quotations/{quotation.id}/reject/',
            {'lost_reason': 'Too expensive'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        quotation.refresh_from_db()
        lead.refresh_from_db()
        self.assertEqual(quotation.status, 'rejected')
        self.assertEqual(lead.status, 'lost')

    def test_start_production_from_sales_order(self):
        sales_order = SalesOrder.objects.create(
            employee=self.admin, customer=self.customer, date=date(2026, 8, 1),
        )
        SalesOrderItem.objects.create(
            order=sales_order, product=self.product, quantity=2,
            unit_price=800, amount=1600,
        )
        response = self.client.post(
            f'/api/sales/orders/{sales_order.id}/start-production/',
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['job_orders']), 1)
        self.assertEqual(JobOrder.objects.filter(sales_order=sales_order).count(), 1)

    def test_delivery_note_creates_invoice(self):
        delivery_note = DeliveryNote.objects.create(
            customer=self.customer, invoice_date=date(2026, 8, 10),
        )
        from apps.sales.models import DeliveryNoteItem
        DeliveryNoteItem.objects.create(
            delivery_note=delivery_note, product=self.product,
            quantity=2, unit_price=800, amount=1600,
        )
        delivery_note.recalculate_total()
        response = self.client.post(
            f'/api/sales/delivery-notes/{delivery_note.id}/create-invoice/',
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['invoice_number'].startswith('INV-'))

    def test_invoice_mark_paid(self):
        from apps.invoices.models import Invoice
        invoice = Invoice.objects.create(
            invoice_number='INV-9999', customer_name='Acme Corp',
            invoice_date=date(2026, 8, 10), due_date=date(2026, 8, 25),
            total=1000, status='sent',
        )
        response = self.client.post(
            f'/api/invoices/invoices/{invoice.id}/mark-paid/',
            {'method': 'cheque', 'reference_number': 'CHQ-001'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'paid')

    def test_job_order_check_stock_and_issue(self):
        job_order = JobOrder.objects.create(
            customer=self.customer, product=self.product, quantity=2,
            start_date=date(2026, 8, 10), bom=self.bom,
        )
        response = self.client.post(
            f'/api/production/job-orders/{job_order.id}/check-stock/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['requirements'][0]['status'], 'available')

        response = self.client.post(
            f'/api/production/job-orders/{job_order.id}/issue-material/',
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MaterialIssueSlip.objects.count(), 1)

    def test_check_stock_reports_short_for_product_without_bom(self):
        Product.objects.filter(pk=self.product.pk).update(quantity=26)
        job_order = JobOrder.objects.create(
            customer=self.customer, product=self.product, quantity=40,
            start_date=date(2026, 8, 10),
        )
        response = self.client.post(
            f'/api/production/job-orders/{job_order.id}/check-stock/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['requirements']), 1)
        self.assertEqual(response.data['requirements'][0]['status'], 'short')
        self.assertEqual(
            response.data['requirements'][0]['available_quantity'], 26.0,
        )

    def test_grn_inspect_populates_product_and_quantity(self):
        grn = GoodsReceiptNote.objects.create(
            purchase_order=None,
            supplier=None,
            warehouse=self.warehouse,
            received_date=date(2026, 8, 12),
            status='received',
        )
        GRNItem.objects.create(grn=grn, product=self.product, quantity=5)
        GRNItem.objects.create(grn=grn, product=self.raw, quantity=10)
        response = self.client.post(
            f'/api/production/grns/{grn.id}/inspect/',
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 2)
        by_product = {item['product_name']: item for item in response.data}
        self.assertEqual(by_product[self.product.name]['quantity'], '5.00')
        self.assertEqual(by_product[self.raw.name]['quantity'], '10.00')
        self.assertTrue(all(item['inspection_no'] for item in response.data))

    def test_receive_grn_marks_purchase_order_received(self):
        vendor = Vendor.objects.create(name='Test Supplier')
        purchase_order = PurchaseOrder.objects.create(
            vendor=vendor, order_date=date(2026, 8, 1), status='pending',
        )
        grn = GoodsReceiptNote.objects.create(
            purchase_order=purchase_order,
            supplier=vendor,
            warehouse=self.warehouse,
            received_date=date(2026, 8, 12),
            status='received',
        )
        GRNItem.objects.create(
            grn=grn, product=self.raw, quantity=5,
        )
        response = self.client.post(
            f'/api/production/grns/{grn.id}/receive/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        purchase_order.refresh_from_db()
        self.assertEqual(purchase_order.status, 'received')
        self.assertEqual(
            purchase_order.actual_delivery_date, date(2026, 8, 12),
        )

    def test_unauthenticated_access_rejected(self):
        anon = APIClient()
        response = anon.get('/api/production/job-orders/')
        self.assertEqual(response.status_code, 401)
