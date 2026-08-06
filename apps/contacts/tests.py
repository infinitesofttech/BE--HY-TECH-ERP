from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Company, Contact


class ContactModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='owner', email='owner@contacts.test',
            password='testpass123', role='super_admin',
        )
        self.company = Company.objects.create(name='Acme Corp')

    def test_new_fields_defaults(self):
        contact = Contact.objects.create(
            first_name='John', last_name='Doe', company=self.company,
        )
        self.assertEqual(contact.type, 'person')
        self.assertEqual(contact.about, '')
        self.assertEqual(contact.visibility, 'public')
        self.assertEqual(contact.name, 'John Doe')

    def test_visibility_selected_and_visible_to(self):
        contact = Contact.objects.create(
            first_name='Jane', last_name='Smith',
            type='business', about='Key partner',
            visibility='selected',
        )
        contact.visible_to.add(self.user)
        self.assertEqual(contact.visible_to.count(), 1)
        self.assertEqual(
            list(contact.visible_to.all()), [self.user],
        )


class ContactAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='admin', email='admin@contacts.test',
            password='testpass123', role='super_admin',
        )
        self.peer = User.objects.create_user(
            username='peer', email='peer@contacts.test',
            password='testpass123', role='msr',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.company = Company.objects.create(name='Acme Corp')

    def test_create_contact_with_new_fields(self):
        response = self.client.post('/api/contacts/contacts/', {
            'first_name': 'Alice',
            'last_name': 'Cooper',
            'job_title': 'CTO',
            'type': 'business',
            'about': 'Decision maker',
            'company': self.company.id,
            'visibility': 'selected',
            'visible_to': [self.peer.id],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['type'], 'business')
        self.assertEqual(response.data['about'], 'Decision maker')
        self.assertEqual(response.data['visibility'], 'selected')
        self.assertEqual(response.data['name'], 'Alice Cooper')
        self.assertIn('peer@contacts.test', response.data['visible_to_names'])

    def test_list_filter_by_type_and_search(self):
        Contact.objects.create(
            first_name='Bob', last_name='Jones', type='person',
        )
        Contact.objects.create(
            first_name='Widget', last_name='Co', type='business',
        )
        response = self.client.get('/api/contacts/contacts/?type=business')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['last_name'], 'Co')

        response = self.client.get('/api/contacts/contacts/?search=Jones')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['last_name'], 'Jones')
