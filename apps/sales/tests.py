from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Customer, CustomerFeedback


class CustomerFeedbackModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Jane Corp')

    def test_feedback_default_status(self):
        feedback = CustomerFeedback.objects.create(
            customer=self.customer, subject='Great service',
            feedback='Loved the product.',
        )
        self.assertEqual(feedback.status, 'pending')


class CustomerFeedbackAPITests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username='admin', email='admin@sales.test',
            password='testpass123', role='super_admin',
        )
        self.customer = Customer.objects.create(name='Jane Corp')
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_create_feedback(self):
        response = self.client.post('/api/sales/feedback/', {
            'customer': self.customer.id,
            'subject': 'Support ticket',
            'feedback': 'Needs follow up',
            'date': '2026-07-01',
            'status': 'in_review',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['customer_name'], 'Jane Corp')
        self.assertEqual(response.data['status'], 'in_review')

    def test_list_feedback_filter_by_status_and_search(self):
        CustomerFeedback.objects.create(
            customer=self.customer, subject='Praise',
            feedback='Excellent', status='resolved',
        )
        CustomerFeedback.objects.create(
            customer=self.customer, subject='Complaint',
            feedback='Slow delivery', status='pending',
        )
        response = self.client.get('/api/sales/feedback/?status=pending')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['subject'], 'Complaint')

        response = self.client.get('/api/sales/feedback/?search=Praise')
        self.assertEqual(len(response.data['results']), 1)

    def test_detail_update(self):
        feedback = CustomerFeedback.objects.create(
            customer=self.customer, subject='Old', feedback='Old text',
        )
        response = self.client.patch(
            f'/api/sales/feedback/{feedback.pk}/',
            {'status': 'resolved'}, format='json',
        )
        self.assertEqual(response.status_code, 200)
        feedback.refresh_from_db()
        self.assertEqual(feedback.status, 'resolved')
