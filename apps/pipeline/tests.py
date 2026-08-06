from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.contacts.models import Contact
from .models import Pipeline, PipelineStage, Lead, Deal


class LeadModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='owner', email='owner@pipeline.test',
            password='testpass123', role='super_admin',
        )

    def test_first_last_name_and_name_property(self):
        lead = Lead.objects.create(
            first_name='John', last_name='Doe', lead_type='person',
            owner=self.user,
        )
        self.assertEqual(lead.name, 'John Doe')

    def test_lead_type_organization(self):
        lead = Lead.objects.create(
            first_name='Widget', last_name='Inc', lead_type='organization',
        )
        self.assertEqual(lead.lead_type, 'organization')

    def test_lead_visibility_selected(self):
        lead = Lead.objects.create(
            first_name='Jane', last_name='Smith', visibility='selected',
        )
        lead.visible_to.add(self.user)
        self.assertEqual(lead.visible_to.count(), 1)


class DealModelTests(TestCase):
    def setUp(self):
        self.stage = PipelineStage.objects.create(name='Demo', probability_default=50)

    def test_progress_and_status_defaults(self):
        deal = Deal.objects.create(name='Big Deal', pipeline_stage=self.stage)
        self.assertEqual(deal.progress, 'qualification')
        self.assertEqual(deal.status, 'open')

    def test_progress_choices(self):
        deal = Deal.objects.create(
            name='Closed Deal', progress='won', status='closed',
            pipeline_stage=self.stage,
        )
        self.assertEqual(deal.get_progress_display(), 'Won')


class PipelineModelTests(TestCase):
    def test_pipeline_action_default(self):
        pipeline = Pipeline.objects.create(name='Sales')
        self.assertEqual(pipeline.action, 'all')
        self.assertEqual(pipeline.status, 'active')


class PipelineAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='admin', email='admin@pipeline.test',
            password='testpass123', role='super_admin',
        )
        self.peer = User.objects.create_user(
            username='peer', email='peer@pipeline.test',
            password='testpass123', role='msr',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.stage = PipelineStage.objects.create(name='Qualification', probability_default=20)

    def test_create_lead(self):
        response = self.client.post('/api/pipeline/leads/', {
            'first_name': 'Alice',
            'last_name': 'Walker',
            'lead_type': 'person',
            'company_name': 'Walker LLC',
            'visibility': 'selected',
            'visible_to': [self.peer.id],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Alice Walker')
        self.assertEqual(response.data['lead_type'], 'person')
        self.assertIn('peer@pipeline.test', response.data['visible_to_names'])

    def test_list_leads_search_by_last_name(self):
        Lead.objects.create(first_name='Bob', last_name='Martin')
        Lead.objects.create(first_name='Carol', last_name='Walker')
        response = self.client.get('/api/pipeline/leads/?search=Walker')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['last_name'], 'Walker')

    def test_create_deal_with_progress_and_status(self):
        response = self.client.post('/api/pipeline/deals/', {
            'name': 'Enterprise Deal',
            'value': '50000',
            'pipeline_stage': self.stage.id,
            'progress': 'proposal',
            'status': 'in_progress',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['progress'], 'proposal')
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertEqual(response.data['progress_name'], 'Proposal')

    def test_filter_deals_by_progress(self):
        Deal.objects.create(
            name='One', progress='proposal', pipeline_stage=self.stage,
        )
        Deal.objects.create(
            name='Two', progress='demo', pipeline_stage=self.stage,
        )
        response = self.client.get('/api/pipeline/deals/?progress=proposal')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'One')

    def test_create_pipeline_with_action(self):
        response = self.client.post('/api/pipeline/pipelines/', {
            'name': 'Partner Pipeline',
            'action': 'selected',
            'status': 'active',
            'stages': [self.stage.id],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['action'], 'selected')
