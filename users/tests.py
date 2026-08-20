from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTests(APITestCase):
    def test_register_success(self):
        url = reverse('register')
        data = {'username': 'bob', 'email': 'bob@test.com', 'password': 'StrongPass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_register_password_not_returned(self):
        url = reverse('register')
        data = {'username': 'bob', 'email': 'bob@test.com', 'password': 'StrongPass123'}
        response = self.client.post(url, data)
        self.assertNotIn('password', response.data)

    def test_register_default_role_is_client(self):
        url = reverse('register')
        data = {'username': 'bob', 'email': 'bob@test.com', 'password': 'StrongPass123'}
        self.client.post(url, data)
        user = User.objects.get(username='bob')
        self.assertEqual(user.role, User.Role.CLIENT)

    def test_register_weak_password_rejected(self):
        url = reverse('register')
        data = {'username': 'bob', 'email': 'bob@test.com', 'password': '123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='ali', email='ali@test.com', password='StrongPass123'
        )

    def test_login_success(self):
        url = reverse('login')
        response = self.client.post(url, {'username': 'ali', 'password': 'StrongPass123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        url = reverse('login')
        response = self.client.post(url, {'username': 'ali', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='ali', email='ali@test.com', password='StrongPass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_profile_authenticated(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'ali')

    def test_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)