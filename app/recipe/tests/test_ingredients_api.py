from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


URL_INGREDIENTS = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Tests for unauthenticated Ingredients API accesses."""

    def setUp(self):
        """SetUp function is run before every test."""

        self.client = APIClient()

    def test_login_required_to_retrieve_ingredients(self):
        """Tests that login is required for retrieving ingredients."""

        # Retrieve the ingredients belonging to user.
        response = self.client.get(URL_INGREDIENTS)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Tests for authenticated Ingredients API accesses."""

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

        # Retrieve ingredients from the database.
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

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Tests filtering ingredients by those assigned to recipes."""

        # Create two tags, assign one of them to a recipe
        # while leaving the other one unassigned.
        ingredient1 = Ingredient.objects.create(user=self.user, name='Apple')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Turkey')

        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=5.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        response = self.client.get(URL_INGREDIENTS, {'assigned_only': True})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        # The response should only include the ingredent1.
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Tests filtering ingredients by assigned returns unique items."""

        ingredient = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Parmaggiano Cheese')

        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=30,
            price=12.00,
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Coriander Eggs on Toast',
            time_minutes=20,
            price=5.00,
            user=self.user
        )

        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        response = self.client.get(URL_INGREDIENTS, {'assigned_only': True})

        self.assertEqual(len(response.data), 1)
