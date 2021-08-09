from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


URL_INGREDIENTS = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """API tests for publicly available ingredients."""

    def setUp(self):
        """SetUp function is run before every test."""

        self.client = APIClient()

    def test_login_required_to_retrieve_ingredients(self):
        """Tests that login is required for retrieving ingredients."""

        # Retrieve the ingredients belonging to user.
        response = self.client.get(URL_INGREDIENTS)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """API tests for available ingredients to authorized users."""

    def setUp(self):
        """SetUp function is run before every test."""

        credentials = {'email': 'testuser@gmail.com', 'password': 'Testpass12'}
        self.user = get_user_model().objects.create_user(**credentials)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Tests retrieving a list of ingredients."""

        Ingredient.objects.create(user=self.user, name='Egg')
        Ingredient.objects.create(user=self.user, name='Salt')

        # Retrieve the ingredients belonging to user.
        response = self.client.get(URL_INGREDIENTS)

        # Ensure ingredients are returned in reversed order based on name.
        ingredients = Ingredient.objects.all().order_by('-name')

        # Create an ingredient serializer allowing more than one items.
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_authenticated_user(self):
        """Tests that retrieved ingredients are
        limited to authenticated users."""

        # Create a new user addition to the user created in
        # setup, and leave it without an authentication.
        credentials = {'email': 'newuser@gmail.com', 'password': 'Testpass34'}
        new_user = get_user_model().objects.create_user(**credentials)

        # Create an ingredient that is assigned to the new user.
        Ingredient.objects.create(user=new_user, name='Vinegar')

        # Create an ingredient that is assigned to the authenticated user.
        ingredient = Ingredient.objects.create(user=self.user, name='Curry')

        response = self.client.get(URL_INGREDIENTS)

        # Check that the response code is HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response includes only one ingredient.
        self.assertEqual(len(response.data), 1)

        # Check that the name of the returned ingredient matches with the
        # name of the ingredient that was assigned to the authenticated user.
        self.assertEqual(response.data[0]['name'], ingredient.name)

    def test_create_ingredient(self):
        """Tests new ingredient creation."""

        ingredient_payload = {'name': 'Test Ingredient'}
        self.client.post(URL_INGREDIENTS, ingredient_payload)

        is_ingredient_created = Ingredient.objects.filter(
            user=self.user,
            name=ingredient_payload['name']
        ).exists()
        self.assertTrue(is_ingredient_created)

    def test_create_ingredient_invalid_payload(self):
        """Tests creating a new ingredient with invalid payload."""

        ingredient_payload = {'name': ''}
        response = self.client.post(URL_INGREDIENTS, ingredient_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
