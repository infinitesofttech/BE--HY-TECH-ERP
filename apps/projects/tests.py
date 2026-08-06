from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import (
    Project, Task, Timesheet, Milestone, ResourceAllocation,
)


class ProjectsModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='manager', email='manager@proj.test',
            password='testpass123', role='manager',
        )
        self.project = Project.objects.create(
            name='Website Redesign', due_date='2026-12-31', budget=1000,
            team_leader=self.user,
        )
        self.task = Task.objects.create(
            title='Build landing page', project=self.project,
        )
        self.milestone = Milestone.objects.create(
            project=self.project, name='Design', owner=self.user,
            date='2026-09-01', progress=50,
        )

    def test_task_status_default_active(self):
        self.assertEqual(self.task.status, 'active')

    def test_timesheet_used_hours(self):
        ts = Timesheet.objects.create(
            user=self.user, project=self.project, task=self.task,
            date='2026-08-01', used_hours=Decimal('4.50'),
        )
        self.assertEqual(ts.used_hours, Decimal('4.50'))

    def test_resource_allocation(self):
        ra = ResourceAllocation.objects.create(
            resource=self.user, role='Developer', project=self.project,
            hours=40, allocated=75, availability=25,
        )
        self.assertEqual(ra.allocated, Decimal('75'))
        self.assertEqual(ra.project, self.project)


class ProjectsAPITests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username='admin', email='admin@proj.test',
            password='testpass123', role='super_admin',
        )
        self.project = Project.objects.create(
            name='Website Redesign', due_date='2026-12-31', budget=1000,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_create_project_with_new_status(self):
        response = self.client.post('/api/projects/projects/', {
            'name': 'Mobile App',
            'priority': 'high',
            'status': 'active',
            'due_date': '2026-11-30',
            'description': 'Build the mobile app',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'active')

    def test_task_with_project(self):
        response = self.client.post('/api/projects/tasks/', {
            'title': 'Fix bugs',
            'project': self.project.id,
            'priority': 'high',
            'status': 'active',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['project_name'], 'Website Redesign')

    def test_timesheet_uses_used_hours(self):
        task = Task.objects.create(title='Task 1', project=self.project)
        response = self.client.post('/api/projects/timesheets/', {
            'user': self.admin.id,
            'project': self.project.id,
            'task': task.id,
            'date': '2026-08-01',
            'used_hours': '4.00',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['used_hours'], '4.00')

    def test_milestone_with_owner(self):
        response = self.client.post('/api/projects/milestones/', {
            'project': self.project.id,
            'name': 'Launch',
            'owner': self.admin.id,
            'date': '2026-12-01',
            'progress': 20,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['owner_name'], 'admin@proj.test')
        self.assertEqual(response.data['date'], '2026-12-01')

    def test_resource_allocation_crud(self):
        response = self.client.post('/api/projects/resource-allocations/', {
            'resource': self.admin.id,
            'role': 'Designer',
            'project': self.project.id,
            'hours': '20',
            'allocated': '50',
            'availability': '50',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        pk = response.data['id']

        response = self.client.get(
            f'/api/projects/resource-allocations/{pk}/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['project_name'], 'Website Redesign')

        response = self.client.delete(
            f'/api/projects/resource-allocations/{pk}/'
        )
        self.assertEqual(response.status_code, 204)

    def test_project_analytics(self):
        Milestone.objects.create(
            project=self.project, name='Design', progress=100,
        )
        Milestone.objects.create(
            project=self.project, name='Dev', progress=0,
        )
        Timesheet.objects.create(
            user=self.admin, project=self.project, date='2026-08-01',
            used_hours=Decimal('2.00'),
        )
        response = self.client.get('/api/projects/analytics/')
        self.assertEqual(response.status_code, 200)
        row = response.data[0]
        self.assertEqual(row['project'], 'Website Redesign')
        self.assertEqual(row['progress'], 50.0)
        self.assertEqual(Decimal(row['budget']), Decimal('1000'))
        self.assertEqual(Decimal(row['spent']), Decimal('2.00'))
        self.assertEqual(row['health'], 'on_track')
