from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Ticket, TicketHistory

User = get_user_model()


class CategoryTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com', password='pass12345', role=User.Role.ADMIN
        )
        self.client_user = User.objects.create_user(
            username='client1', email='client1@test.com', password='pass12345'
        )

    def test_admin_can_create_category(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('category-list')
        response = self.client.post(url, {'name': 'Texnik muammo'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_client_cannot_create_category(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('category-list')
        response = self.client.post(url, {'name': 'Texnik muammo'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_can_read_categories(self):
        Category.objects.create(name='Texnik muammo')
        self.client.force_authenticate(user=self.client_user)
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_duplicate_category_name_rejected(self):
        Category.objects.create(name='Texnik muammo')
        self.client.force_authenticate(user=self.admin)
        url = reverse('category-list')
        response = self.client.post(url, {'name': 'Texnik muammo'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TicketTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com', password='pass12345', role=User.Role.ADMIN
        )
        self.operator = User.objects.create_user(
            username='operator1', email='op1@test.com', password='pass12345', role=User.Role.OPERATOR
        )
        self.client1 = User.objects.create_user(
            username='client1', email='client1@test.com', password='pass12345'
        )
        self.client2 = User.objects.create_user(
            username='client2', email='client2@test.com', password='pass12345'
        )
        self.category = Category.objects.create(name='Texnik muammo')

    def test_client_can_create_ticket(self):
        self.client.force_authenticate(user=self.client1)
        url = reverse('ticket-list')
        data = {'title': 'Muammo', 'description': 'Tavsif', 'category': self.category.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['client'], self.client1.id)

    def test_client_sees_only_own_tickets(self):
        Ticket.objects.create(title='T1', description='D1', client=self.client1)
        Ticket.objects.create(title='T2', description='D2', client=self.client2)
        self.client.force_authenticate(user=self.client1)
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 1)

    def test_admin_sees_all_tickets(self):
        Ticket.objects.create(title='T1', description='D1', client=self.client1)
        Ticket.objects.create(title='T2', description='D2', client=self.client2)
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 2)

    def test_operator_sees_only_assigned_tickets(self):
        Ticket.objects.create(title='T1', description='D1', client=self.client1, operator=self.operator)
        Ticket.objects.create(title='T2', description='D2', client=self.client2)
        self.client.force_authenticate(user=self.operator)
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 1)

    def test_client_cannot_change_status(self):
        ticket = Ticket.objects.create(title='T1', description='D1', client=self.client1)
        self.client.force_authenticate(user=self.client1)
        url = reverse('ticket-detail', args=[ticket.id])
        response = self.client.patch(url, {'status': 'resolved'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_assign_operator(self):
        ticket = Ticket.objects.create(title='T1', description='D1', client=self.client1)
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-detail', args=[ticket.id])
        response = self.client.patch(url, {'operator': self.operator.id, 'status': 'in_progress'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_status_change_creates_history(self):
        ticket = Ticket.objects.create(title='T1', description='D1', client=self.client1)
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-detail', args=[ticket.id])
        self.client.patch(url, {'status': 'in_progress'})
        self.assertEqual(TicketHistory.objects.filter(ticket=ticket).count(), 1)

    def test_resolved_at_set_automatically(self):
        ticket = Ticket.objects.create(title='T1', description='D1', client=self.client1)
        self.client.force_authenticate(user=self.admin)
        url = reverse('ticket-detail', args=[ticket.id])
        response = self.client.patch(url, {'status': 'resolved'})
        self.assertIsNotNone(response.data['resolved_at'])

    def test_unauthenticated_cannot_access(self):
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ticket_status_filter(self):
        Ticket.objects.create(title='T1', description='D1', client=self.client1, status=Ticket.Status.RESOLVED)
        Ticket.objects.create(title='T2', description='D2', client=self.client1, status=Ticket.Status.NEW)
        self.client.force_authenticate(user=self.client1)
        url = reverse('ticket-list') + '?status=resolved'
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 1)

    def test_ticket_search(self):
        Ticket.objects.create(title='Login xato', description='D1', client=self.client1)
        Ticket.objects.create(title='Boshqa muammo', description='D2', client=self.client1)
        self.client.force_authenticate(user=self.client1)
        url = reverse('ticket-list') + '?search=Login'
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 1)

    def test_pagination_format(self):
        Ticket.objects.create(title='T1', description='D1', client=self.client1)
        self.client.force_authenticate(user=self.client1)
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertIn('count', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('current_page', response.data)