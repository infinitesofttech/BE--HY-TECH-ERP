from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Holiday

User = get_user_model()


class HolidayAPITests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@calendar.test',
            password='testpass123', role='super_admin',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_holiday_create_with_description_type_and_status(self):
        response = self.client.post(
            '/api/calendar/holidays/',
            {
                'name': 'Republic Day', 'date': '2026-01-26',
                'description': 'National holiday', 'type': 'public',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['type'], 'public')
        self.assertEqual(response.data['description'], 'National holiday')
        self.assertEqual(response.data['holiday_status'], 'past')

        today = date.today()
        end_of_week = today + timedelta(days=(6 - today.weekday()))
        soon = today + timedelta(days=1)
        expected_soon = 'this_week' if soon <= end_of_week else 'upcoming'

        response = self.client.post(
            '/api/calendar/holidays/',
            {'name': 'Local Fest', 'date': soon.isoformat()},
            format='json',
        )
        self.assertEqual(response.data['holiday_status'], expected_soon)

        far = today + timedelta(days=40)
        response = self.client.post(
            '/api/calendar/holidays/',
            {'name': 'Deepavali', 'date': far.isoformat(), 'type': 'government'},
            format='json',
        )
        self.assertEqual(response.data['holiday_status'], 'upcoming')
        self.assertEqual(response.data['type'], 'government')

    def test_holiday_update_and_filter(self):
        Holiday.objects.create(
            name='New Year', date=date(2026, 1, 1), type='public',
        )
        Holiday.objects.create(
            name='Independence Day', date=date(2026, 8, 15), type='public',
        )
        response = self.client.get('/api/calendar/holidays/?year=2026')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

        holiday = Holiday.objects.get(name='New Year')
        response = self.client.patch(
            f'/api/calendar/holidays/{holiday.id}/',
            {'description': 'First day of the year'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['description'], 'First day of the year',
        )
