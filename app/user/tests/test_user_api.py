"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """ Create a user"""
    return get_user_model().objects.create_user(**params)


class PublicUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()


    def test_create_user_success(self):
        """Test creating user"""
        payload = {
            'email': 'test@example.com',
            'password': 'test123',
            'name': 'name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


    def test_user_with_email_error(self):
        payload = {
            'email': 'test@gmail.com',
            'password': '1234567',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_pass_short(self):
        payload = {
            'email': 'test@gmail.com',
            'password': '123',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        is_exist = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(is_exist)


    def test_create_token(self):
        payload = {
            'email': 'test@gmail.com',
            'password': '123456',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)


    def test_create_token_bad_credentials(self):
        payload = {
            'email': 'test@gmail.com',
            'password': '123456',
        }
        create_user(**payload)
        payload['password'] = 'wrong'
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)


    def test_create_token_email_not_found(self):
        payload = {
            'email': 'test@gmail.com',
            'password': '123456',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)


    def test_create_token_blank_password(self):
        payload = {
            'email': 'test@gmail.com',
            'password': '123456',
        }
        create_user(**payload)
        payload['password'] = ''
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)


    def test_profile_unauthorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserTest(TestCase):
    def setUp(self):
        self.user = create_user(email='test@gmail.com', password='123456', name='name')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_profile_success(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.data, {'name': self.user.name, 'email': self.user.email,})
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_post_me_unallowed(self):
        res = self.client.post(ME_URL,{})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_update_user_profile(self):
        payload = {'password': 'newPass'}
        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['password']))
