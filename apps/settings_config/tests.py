from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Department, Designation

User = get_user_model()


class DepartmentAPITests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@settings.test',
            password='testpass123', role='super_admin',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_department_create_list_and_employee_count(self):
        response = self.client.post(
            '/api/settings/departments/',
            {'name': 'Sales', 'description': 'Sales team', 'status': 'active'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        dept_id = response.data['id']
        self.assertEqual(response.data['status'], 'active')

        User.objects.create_user(
            username='e1', email='e1@test.com', password='pass12345',
            role='msr', department_id=dept_id,
        )
        User.objects.create_user(
            username='e2', email='e2@test.com', password='pass12345',
            role='msr', department_id=dept_id,
        )

        response = self.client.get('/api/settings/departments/')
        self.assertEqual(response.status_code, 200)
        dept = next(d for d in response.data['results'] if d['id'] == dept_id)
        self.assertEqual(dept['employee_count'], 2)

    def test_department_update_and_delete(self):
        dept = Department.objects.create(name='Support')
        head = User.objects.create_user(
            username='head', first_name='Head',
            email='head@test.com', password='pass12345',
            role='manager',
        )
        response = self.client.patch(
            f'/api/settings/departments/{dept.id}/',
            {'department_head': head.id, 'status': 'inactive'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['department_head'], head.id)
        self.assertEqual(response.data['department_head_name'], 'Head')
        self.assertEqual(response.data['status'], 'inactive')

        response = self.client.delete(f'/api/settings/departments/{dept.id}/')
        self.assertEqual(response.status_code, 204)


class DesignationAPITests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@settings.test',
            password='testpass123', role='super_admin',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_designation_crud_with_employee_count(self):
        dept = Department.objects.create(name='Engineering')
        response = self.client.post(
            '/api/settings/designations/',
            {'name': 'Software Engineer', 'department': dept.id, 'status': 'active'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        des_id = response.data['id']

        User.objects.create_user(
            username='eng', email='eng@test.com', password='pass12345',
            role='msr', designation_id=des_id,
        )
        response = self.client.get('/api/settings/designations/')
        self.assertEqual(response.status_code, 200)
        des = next(d for d in response.data['results'] if d['id'] == des_id)
        self.assertEqual(des['employee_count'], 1)
        self.assertEqual(des['department_name'], 'Engineering')

        response = self.client.patch(
            f'/api/settings/designations/{des_id}/',
            {'status': 'inactive'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'inactive')

        response = self.client.delete(f'/api/settings/designations/{des_id}/')
        self.assertEqual(response.status_code, 204)

