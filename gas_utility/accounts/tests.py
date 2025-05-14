from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class AccountTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.login_url = '/api/accounts/login/'
        self.logout_url = '/api/accounts/logout/'
        self.register_url = '/api/accounts/register/'
        self.profile_url = '/api/accounts/profile/'
        self.change_password_url = '/api/accounts/change-password/'

    def get_tokens(self):
        refresh = RefreshToken.for_user(self.user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

    def test_login_success(self):
        data = {'username': 'testuser', 'password': 'testpass'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_failure(self):
        data = {'username': 'wronguser', 'password': 'wrongpass'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_profile_get(self):
        tokens = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_profile_update(self):
        tokens = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
        response = self.client.put(self.profile_url, {'username': 'updateduser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'updateduser')

    def test_change_password(self):
        tokens = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
        data = {
            'old_password': 'testpass',
            'new_password': 'newsecurepass123'
        }
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        tokens = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
        data = {
            'refresh': tokens['refresh']
        }
        response = self.client.post(self.logout_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
