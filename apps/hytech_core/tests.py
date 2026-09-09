from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class HytechIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command('seed_hytech_data')

    def setUp(self):
        self.client = APIClient()

    def test_01_staff_login(self):
        res = self.client.post('/auth/staff/login/', {'username': 'staff', 'password': 'Staff@123'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', res.data)
        self.assertIn('access', res.data['tokens'])
        self.assertEqual(res.data['user_type'], 'employee')

    def test_02_admin_login(self):
        res = self.client.post('/auth/staff/login/', {'username': 'admin', 'password': 'Admin@123'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['user_type'], 'admin')

    def test_03_customer_login(self):
        res = self.client.post('/auth/customer/login/', {'mobile_number': '6789012345'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['user_type'], 'customer')
        self.assertEqual(res.data['customer']['family_id'], 'HTF-000001')

    def test_04_customer_endpoints(self):
        # List customers
        res = self.client.get('/customers/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data if isinstance(res.data, list) else res.data.get('results', [])
        self.assertGreaterEqual(len(data), 1)

        # Customer detail
        res = self.client.get('/customers/HTF-000001/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['family_id'], 'HTF-000001')

        # Family members
        res = self.client.get('/customers/HTF-000001/family-members/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        m_data = res.data if isinstance(res.data, list) else res.data.get('results', [])
        self.assertGreaterEqual(len(m_data), 1)

    def test_05_services_and_catalog(self):
        # Base Services
        res = self.client.get('/services/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        s_data = res.data if isinstance(res.data, list) else res.data.get('results', [])
        self.assertEqual(len(s_data), 45)

        # Sub Services
        res = self.client.get('/services/sub-services/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_06_service_visits(self):
        res = self.client.get('/customers/service-visits/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        v_data = res.data if isinstance(res.data, list) else res.data.get('results', [])
        self.assertGreaterEqual(len(v_data), 1)

        # Visit detail
        res = self.client.get('/customers/service-visits/VIS-000001/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('documents', res.data)

    def test_07_reminders_and_followups(self):
        res = self.client.get('/reminders/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get('/reminders/RMD-000001/follow-ups/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_08_pending_work_and_summary(self):
        res = self.client.get('/pending-work/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get('/pending-work/summary/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('total', res.data)
        self.assertIn('pending', res.data)

    def test_09_dashboard(self):
        res = self.client.get('/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('today_summary', res.data)
        self.assertIn('business_summary', res.data)
        self.assertIn('customer_summary', res.data)

    def test_10_applications(self):
        res = self.client.get('/applications/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get('/applications/APP-000001/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get('/applications/APP-000001/timeline/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_11_hrms_and_demographics(self):
        res = self.client.get('/hrms/attendance/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get('/hrms/leaves/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get('/hrms/holidays/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get('/villages/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get('/villages/family-tree/HTF-000001/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('head', res.data)

        res = self.client.get('/audit-logs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get('/inquiries/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
