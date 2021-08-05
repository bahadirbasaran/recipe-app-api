from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """Test a new user creation with an e-mail"""

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
        """Test an email normalization of a new user"""

        email = 'testuser@GMAIL.com'

        user = get_user_model().objects.create_user(
            email=email,
            password='Testpass123'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test a new user creation with a blank e-mail. Should passing None
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

        # The field is_superuser is inherited from PermissionsMixin
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
