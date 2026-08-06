from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.finance.models import Tax
from apps.products.models import Product, ProductCategory
from apps.purchases.models import (
    Vendor,
    Purchase,
    PurchaseOrder,
    PurchaseReturn,
    PurchaseItem,
    PurchaseOrderItem,
    PurchaseReturnItem,
)


class PurchaseModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='admin',
            email='admin@purchases.test',
            password='testpass123',
            role='super_admin',
        )
        self.vendor = Vendor.objects.create(name='Supplier A', country='CN')
        category = ProductCategory.objects.create(name='Parts')
        self.product = Product.objects.create(
            name='Brake Pad', category=category, price=25,
        )
        self.tax = Tax.objects.create(
            name='VAT', rate=10, status='active', applied_to='both',
        )

    def test_purchase_id_and_total(self):
        purchase = Purchase.objects.create(
            vendor=self.vendor, requestor=self.user, date=date(2026, 7, 1),
            tax=self.tax, shipping_charge=5,
        )
        PurchaseItem.objects.create(
            purchase=purchase, product=self.product,
            quantity=2, unit_price=50, discount=5,
        )
        purchase.recalculate_total()
        self.assertTrue(purchase.purchase_id.startswith('PC-'))
        self.assertEqual(purchase.total_amount, 109.5)

    def test_purchase_order_lead_time_and_on_time(self):
        order = PurchaseOrder.objects.create(
            vendor=self.vendor,
            order_date=date(2026, 1, 1),
            expected_delivery_date=date(2026, 1, 10),
            actual_delivery_date=date(2026, 1, 8),
        )
        self.assertEqual(
            (order.actual_delivery_date - order.order_date).days, 7,
        )
        self.assertTrue(
            order.actual_delivery_date <= order.expected_delivery_date,
        )

    def test_purchase_return_inherits_vendor_from_purchase(self):
        purchase = Purchase.objects.create(
            vendor=self.vendor, date=date(2026, 7, 1),
        )
        purchase_return = PurchaseReturn.objects.create(
            purchase=purchase, return_date=date(2026, 7, 5),
        )
        self.assertEqual(purchase_return.vendor, self.vendor)
        self.assertTrue(purchase_return.return_id.startswith('PR-'))


class PurchaseAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='admin', email='admin@purchases.test',
            password='testpass123', role='super_admin',
        )
        self.client = APIClient()
        self.vendor = Vendor.objects.create(name='Supplier A', country='CN')
        category = ProductCategory.objects.create(name='Parts')
        self.product = Product.objects.create(
            name='Brake Pad', category=category, price=25,
        )
        self.tax = Tax.objects.create(
            name='VAT', rate=10, status='active', applied_to='both',
        )

    def test_analytics_requires_manager_or_above(self):
        response = self.client.get('/api/purchases/analytics/')
        self.assertEqual(response.status_code, 401)

    def test_analytics_payload(self):
        purchase = Purchase.objects.create(
            vendor=self.vendor, requestor=self.admin,
            date=date(2026, 7, 1), tax=self.tax,
        )
        PurchaseItem.objects.create(
            purchase=purchase, product=self.product, quantity=2, unit_price=50,
        )
        purchase.recalculate_total()
        order = PurchaseOrder.objects.create(
            vendor=self.vendor,
            order_date=date(2026, 7, 2),
            expected_delivery_date=date(2026, 7, 12),
            actual_delivery_date=date(2026, 7, 9),
        )
        PurchaseOrderItem.objects.create(
            purchase_order=order, product=self.product,
            quantity=1, unit_price=100,
        )
        order.recalculate_total()

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/purchases/analytics/'
            '?date_from=2026-07-01&date_to=2026-07-31',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_spend'], 110.0)
        self.assertEqual(response.data['suppliers'], 1)
        self.assertEqual(response.data['avg_lead_time_days'], 7.0)
        self.assertEqual(response.data['on_time_percent'], 100.0)
        self.assertEqual(response.data['status'], 'excellent')

    def test_vendor_create_permissions(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            '/api/purchases/vendors/',
            {'name': 'Supplier B'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)

    def test_purchase_create_rejects_empty_items(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            '/api/purchases/',
            {
                'vendor': self.vendor.id,
                'date': '2026-07-01',
                'items': [],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
