from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status


class AdminSiteTests(TestCase):

    def setUp(self):
        """The setUp method is run before every test.
           - Creates a test client that enables making test
             requests to the application in the unit tests.
           - Creates a superuser that is used during tests,
             makes sure the user is logged in to the client.
           - Creates a regular user that is not authenticated
             or that can be list on the admin page.
        """
        self.client = Client()

        self.user_admin = get_user_model().objects.create_superuser(
            email='testsuperuser@gmail.com',
            password='Testpass12'
        )
        self.client.force_login(self.user_admin)

        self.user = get_user_model().objects.create_user(
            email='testuser@gmail.com',
            password='Testpass12',
            name='Test User Full Name'
        )

    def test_user_listing(self):
        """Tests the listing of users on the user page.
           The default user model of Django expects a username,
           however, a custom user model (with email, instead of
           username) was defined in the models.
        """
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_edit_page(self):
        """Tests the user edit page"""

        # A typical URL: /admin/core/user/1 when self.user.id = 1
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_page(self):
        """Tests the create user page"""

        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
