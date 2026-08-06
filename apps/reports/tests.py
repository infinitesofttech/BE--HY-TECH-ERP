from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.sales.models import Customer, SalesOrder


class CustomerAnalyticsAPITests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username='admin', email='admin@reports.test',
            password='testpass123', role='super_admin',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        now = timezone.localdate()
        self.month_start = now.replace(day=1)
        self.prev_month_end = self.month_start - timezone.timedelta(days=1)

        us_a = Customer.objects.create(name='US A', country='United States')
        us_b = Customer.objects.create(name='US B', country='United States')
        de = Customer.objects.create(name='DE C', country='Germany')
        self.old = Customer.objects.create(name='US Old', country='United States')
        Customer.objects.filter(pk=self.old.pk).update(
            created_at=datetime(
                self.prev_month_end.year, self.prev_month_end.month, 1,
                tzinfo=timezone.utc,
            ),
        )

        SalesOrder.objects.create(
            customer=us_a, date=now, status='completed', total_amount=100,
        )
        SalesOrder.objects.create(
            customer=us_a, date=now, status='completed', total_amount=100,
        )
        SalesOrder.objects.create(
            customer=us_b, date=now, status='completed', total_amount=50,
        )
        SalesOrder.objects.create(
            customer=de, date=now, status='cancelled', total_amount=999,
        )
        SalesOrder.objects.create(
            customer=self.old, date=self.prev_month_end,
            status='completed', total_amount=40,
        )

    def test_customer_analytics_totals(self):
        response = self.client.get('/api/reports/customer-analytics/')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['total_customers'], 4)
        self.assertEqual(data['new_this_month'], 3)
        self.assertEqual(data['retention_ratio'], 25.0)
        self.assertEqual(data['avg_ltv'], 72.5)

    def test_customer_analytics_segments(self):
        response = self.client.get('/api/reports/customer-analytics/')
        data = response.data
        segments = {s['segment']: s for s in data['top_customer_segments']}
        us = segments['United States']
        self.assertEqual(us['customers'], 3)
        self.assertEqual(us['revenue'], 290.0)
        self.assertEqual(us['avg_order'], 72.5)
        self.assertEqual(us['growth'], 525.0)

        de = segments['Germany']
        self.assertEqual(de['customers'], 1)
        self.assertEqual(de['revenue'], 0.0)
        self.assertEqual(de['growth'], 0.0)
