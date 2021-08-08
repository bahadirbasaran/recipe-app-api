from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient


URL_CREATE_USER = reverse('user:create')
URL_TOKEN = reverse('user:token')
URL_ME = reverse('user:me')


class PublicUserApiTests(TestCase):
    """Tests API requests that do not require authentication."""

    def setUp(self):
        """SetUp function is run before every test."""

        self.client = APIClient()

    def test_create_valid_user(self):
        """Tests that a user is created successfully with valid credentials."""

        credentials = {
            'email': 'testuser@gmail.com',
            'password': 'Testpass12',
            'name': 'Test Name'
        }
        response = self.client.post(URL_CREATE_USER, credentials)

        # Check that the response is HTTP 201 CREATED.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the object has actually been created properly.
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(credentials['password']))

        # Check that the HTTP response does not include the password.
        self.assertNotIn('password', response.data)

    def test_user_existence(self):
        """Tests the creation of a user that already exists."""

        credentials = {
            'email': 'testuser@gmail.com',
            'password': 'Testpass12',
            'name': 'Test Name'
        }
        get_user_model().objects.create_user(**credentials)

        # Check that this is a bad request since the user has already exists.
        response = self.client.post(URL_CREATE_USER, credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Tests that a password must be more than five characters."""

        credentials = {
            'email': 'testuser@gmail.com',
            'password': 'pw',
            'name': 'Test Name'
        }
        response = self.client.post(URL_CREATE_USER, credentials)

        # Check that this is a bad request since the password was too short.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that user has never been created.
        is_user_created = get_user_model().objects.filter(
            email=credentials['email']
        ).exists()
        self.assertFalse(is_user_created)

    def test_create_token_for_user(self):
        """Tests that a token is created for a registered user"""

        credentials = {'email': 'testuser@gmail.com', 'password': 'Testpass12'}
        get_user_model().objects.create_user(**credentials)

        response = self.client.post(URL_TOKEN, credentials)

        # Response should be a HTTP 200 OK, and should contain a token
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """"Tests that token creation fails if the credentials are invalid."""

        credentials = {'email': 'testuser@gmail.com', 'password': 'Testpass12'}
        get_user_model().objects.create_user(**credentials)

        invalid_credentials = {
            'email': 'testuser@gmail.com',
            'password': 'wrong'
        }
        response = self.client.post(URL_TOKEN, invalid_credentials)

        # Response should be a HTTP 400 BAD REQUEST, and not contain a token
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_not_user(self):
        """Tests that a token is not created if the user does not exist."""

        credentials = {'email': 'testuser@gmail.com', 'password': 'Testpass12'}
        response = self.client.post(URL_TOKEN, credentials)

        # Response should be a HTTP 400 BAD REQUEST, and not contain a token
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Tests that e-mail and password are mandatory for creation."""

        invalid_credentials = {'email': 'testuser@gmail.com', 'password': ''}
        response = self.client.post(URL_TOKEN, invalid_credentials)

        # Response should be a HTTP 400 BAD REQUEST, and not contain a token
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_unauthorized_user(self):
        """Tests that accessing user page without authentication fails."""

        response = self.client.get(URL_ME)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests API requests that require authentication."""

    def setUp(self):
        """SetUp function is run before every test."""

        credentials = {
            'email': 'testuser@gmail.com',
            'password': 'Testpass12',
            'name': 'Test Name'
        }
        self.user = get_user_model().objects.create_user(**credentials)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile(self):
        """Tests retrieving profile of logged in user."""

        response = self.client.get(URL_ME)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user object returns as expected. There is no
        # need (and not secure) to return a password to client side.
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Tests that POST in not allowed on the me url."""

        res = self.client.post(URL_ME)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Tests update of user profile."""

        new_credentials = {'name': 'New Name', 'password': 'NewTestpass12'}
        response = self.client.patch(URL_ME, new_credentials)

        self.user.refresh_from_db()

        # Check that the update is successful.
        self.assertEqual(self.user.name, new_credentials['name'])
        self.assertTrue(self.user.check_password(new_credentials['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
