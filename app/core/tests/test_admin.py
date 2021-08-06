from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        """Setup function is run before every test.
           - Creates a test client that enables making test
             requests to the application in the unit tests.
           - Creates a superuser that is used during tests,
             makes sure of the user is logged in to the client.
           - Creates a regular user that is not authenticated
             or that can be list in the admin page."""

        self.client = Client()

        self.user_admin = get_user_model().objects.create_superuser(
            email='testsuperuser@gmail.com',
            password='Testpass123'
        )
        self.client.force_login(self.user_admin)

        self.user = get_user_model().objects.create_user(
            email='testuser@gmail.com',
            password='Testpass123',
            name='Test User Full Name'
        )

    def test_users_listed(self):
        """Tests the listing of users on user page.
           The default user model of Django expects a username,
           however, a custom user model (with e-mail, instead of
           username) was defined in the models."""

        # Using the reverse instead of typing the URL manually
        # provides flexibility for feature changes in URLs.
        url = reverse('admin:core_user_changelist')

        # Uses the test client to perform a HTTP GET on the url.
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Tests the user edit page"""

        # Typical url: /admin/core/user/1 if self.user.id = 1
        url = reverse('admin:core_user_change', args=[self.user.id])

        response = self.client.get(url)

        # HTTP 200: OK
        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Tests the create user page"""

        url = reverse('admin:core_user_add')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
