from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.settings_config.models import Department, Designation

User = get_user_model()


class EmployeeRegisterTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@accounts.test',
            password='testpass123', role='super_admin',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        self.department = Department.objects.create(name='Sales')
        self.designation = Designation.objects.create(
            name='MSR', department=self.department,
        )

    def test_register_employee_with_hr_fields(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'email': 'new@emp.test',
                'username': 'newemp',
                'first_name': 'New',
                'last_name': 'Employee',
                'password': 'testpass123',
                'role': 'msr',
                'department': self.department.id,
                'designation': self.designation.id,
                'shift_start_time': '09:00',
                'shift_end_time': '17:00',
                'salary': '30000.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['department'], self.department.id)
        self.assertEqual(response.data['designation'], self.designation.id)
        self.assertEqual(response.data['shift_start_time'], '09:00:00')
        self.assertEqual(response.data['shift_end_time'], '17:00:00')
        self.assertEqual(float(response.data['salary']), 30000.0)
        self.assertEqual(response.data['department_name'], 'Sales')
        self.assertEqual(response.data['designation_name'], 'MSR')

    def test_employee_detail_update_with_hr_fields(self):
        employee = User.objects.create_user(
            username='emp', email='emp@accounts.test',
            password='testpass123', role='msr',
        )
        response = self.client.patch(
            f'/api/auth/employees/{employee.id}/',
            {
                'department': self.department.id,
                'designation': self.designation.id,
                'shift_start_time': '10:00',
                'shift_end_time': '19:00',
                'salary': '45000.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['department'], self.department.id)
        self.assertEqual(response.data['shift_start_time'], '10:00:00')
        self.assertEqual(response.data['salary'], '45000.00')

        response = self.client.get(f'/api/auth/employees/{employee.id}/')
        self.assertEqual(response.data['department_name'], 'Sales')
        self.assertEqual(response.data['designation_name'], 'MSR')
