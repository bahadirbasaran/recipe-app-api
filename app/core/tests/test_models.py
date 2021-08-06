# The get_user_model() is provided to return the default user model that
# is configured in settings.py with the line AUTH_USER_MODEL = 'core.User'.
# Essentially, it gives the same output as importing User from core.models.
from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """Tests a new user creation with an e-mail"""

        email = 'testuser@gmail.com'
        password = 'Testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)

        # Passwords cannot be directly compared because of encryption.
        self.assertTrue(user.check_password(password))

    def test_new_user_normalized_email(self):
        """Tests an email normalization of a new user"""

        email = 'testuser@GMAIL.com'

        user = get_user_model().objects.create_user(
            email=email,
            password='Testpass123'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Tests a new user creation with a blank e-mail. Should passing None
           to the e-mail field does not raise a ValueError, the test fails."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='Testpass123'
            )

    def test_create_superuser(self):
        """Test a superuser creation"""

        email = 'testsuperuser@gmail.com'
        password = 'Testpass123'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        # The field is_superuser is inherited from PermissionsMixin.
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
