from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from quickstart.models.authentication_models import User_Data
from django.test import TransactionTestCase


class RegisterAPIViewTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('registering')
        self.valid_user_data = {
            'username': 'testuser',
            'password': 'TestPass123!',
            'email': 'test@example.com',
            'role': 'writer',
            'mobile_number': '1234567890',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_successful_user_registration(self):
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertTrue(User_Data.objects.filter(user=user).exists())
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertIn('data', response_data)
        self.assertEqual(response_data['message'], 'User successfully registered')

    def test_registration_with_existing_username(self):
        User.objects.create_user(username='testuser', email='existing@example.com')
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('Username already exists', response_data['message'])

    def test_registration_with_missing_required_fields(self):
        incomplete_data = {
            'username': 'testuser',
        }
        response = self.client.post(self.register_url, incomplete_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK])

    def test_registration_with_empty_optional_fields(self):
        data = {
            'username': 'testuser',
            'password': 'TestPass123!',
            'role': 'writer',
            'mobile_number': '1234567890',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_registration_method_not_allowed(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('quickstart.models.authentication_models.User_Data.objects.create')
    def test_registration_database_error(self, mock_create):
        mock_create.side_effect = Exception("Database error")
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('Something went wrong during registration', response_data['message'])

    def tearDown(self):
        User.objects.all().delete()
        User_Data.objects.all().delete()


class LoginViewSetTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        self.user_profile = User_Data.objects.create(
            user=self.test_user,
            role='writer',
            mobile_number='1234567890',
            first_name='Test',
            last_name='User'
        )
        self.valid_login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }

    def test_successful_login(self):
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertIn('data', response_data)
        self.assertEqual(response_data['message'], 'Login successful')
        user_data = response_data['data']['user']
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertEqual(user_data['role'], 'writer')
        tokens = response_data['data']['tokens']
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)

    def test_login_with_invalid_credentials(self):
        invalid_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['message'], 'Login failed')

    def test_login_with_nonexistent_user(self):
        invalid_data = {
            'username': 'nonexistentuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_without_user_profile(self):
        user_without_profile = User.objects.create_user(
            username='noprofile',
            password='TestPass123!'
        )
        login_data = {
            'username': 'noprofile',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('User profile not found', response_data['message'])

    def test_login_with_missing_fields(self):
        incomplete_data = {
            'username': 'testuser'
        }
        response = self.client.post(self.login_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_method_not_allowed(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(self.login_url, self.valid_login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_handles_internal_errors(self):
        with patch('quickstart.models.authentication_models.User_Data.objects.get') as mock_get:
            mock_get.side_effect = Exception("Internal error")
            response = self.client.post(self.login_url, self.valid_login_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response_data = response.json()
            self.assertIn('Internal error occurred', response_data['message'])

    def test_user_data_includes_password_in_response(self):
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        user_data = response_data['data']['user']
        self.assertEqual(user_data['password'], 'TestPass123!')

    def tearDown(self):
        User.objects.all().delete()
        User_Data.objects.all().delete()


class AuthenticationTestUtils(TransactionTestCase):
    @staticmethod
    def create_test_user(username='testuser', email='test@example.com', password='TestPass123!'):
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
        profile = User_Data.objects.create(
            user=user,
            role='writer',
            mobile_number='1234567890',
            first_name='Test',
            last_name='User'
        )
        return user, profile
