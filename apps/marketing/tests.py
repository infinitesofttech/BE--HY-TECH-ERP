from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Campaign


class CampaignAPITests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username='admin', email='admin@marketing.test',
            password='testpass123', role='super_admin',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_create_campaign_with_new_fields(self):
        response = self.client.post('/api/marketing/campaigns/', {
            'name': 'Q3 Launch',
            'type': 'pro',
            'status': 'active',
            'deal_value': '10000',
            'target_audience': ['customers', 'leads'],
            'description': 'Quarterly launch campaign',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['type'], 'pro')
        self.assertEqual(response.data['status'], 'active')
        self.assertEqual(response.data['target_audience'], ['customers', 'leads'])

    def test_invalid_target_audience_rejected(self):
        response = self.client.post('/api/marketing/campaigns/', {
            'name': 'Bad Campaign',
            'type': 'basic',
            'target_audience': ['vendors'],
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_archive_and_send(self):
        campaign = Campaign.objects.create(
            name='Email Blast', type='enterprise', status='active',
            created_by=self.admin,
        )
        response = self.client.patch(f'/api/marketing/campaigns/{campaign.pk}/archive/')
        self.assertEqual(response.status_code, 200)
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'archived')

        response = self.client.post(f'/api/marketing/campaigns/{campaign.pk}/send/')
        self.assertEqual(response.status_code, 200)
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'active')
        self.assertIsNotNone(campaign.sent_at)
