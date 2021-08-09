from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


URL_RECIPES = reverse('recipe:recipe-list')


def sample_recipe(user, **parameters):
    """Helper function to create and return a sample recipe."""

    default_parameters = {
        'title': 'Test Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    # Override the parameters or create new ones based on optionals parameters.
    default_parameters.update(parameters)

    return Recipe.objects.create(user=user, **default_parameters)


class PublicRecipeApiTests(TestCase):
    """Tests for unauthenticated Recipe API accesses."""

    def setUp(self):
        """SetUp function is run before every test."""

        self.client = APIClient()

    def test_auth_required(self):
        """Tests that authentication is required for retrieving recipes."""

        # Retrieve the recipes belonging to user.
        response = self.client.get(URL_RECIPES)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Tests for authenticated Recipe API accesses."""

    def setUp(self):
        """SetUp function is run before every test."""

        credentials = {'email': 'testuser@gmail.com', 'password': 'Testpass12'}
        self.user = get_user_model().objects.create_user(**credentials)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Tests retrieving a list of recipes."""

        # Create two recipes.
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        # Retrieve the recipes belonging to user.
        response = self.client.get(URL_RECIPES)

        # Retrieve recipes from the database.
        # Ensure ingredients are returned in reversed order based on id.
        recipes = Recipe.objects.all().order_by('-id')

        # Create a recipe serializer allowing more than one items.
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_authenticated_user(self):
        """Tests that retrieved recipes are limited to authenticated users."""

        # Create a new user addition to the user created in
        # setup, and leave it without an authentication.
        credentials = {'email': 'newuser@gmail.com', 'password': 'Testpass34'}
        new_user = get_user_model().objects.create_user(**credentials)

        # Create a recipe that is assigned to the new user.
        sample_recipe(user=new_user)

        # Create a recipe that is assigned to the authenticated user.
        sample_recipe(user=self.user)

        response = self.client.get(URL_RECIPES)

        # Filter the recipes with the authenticated user.
        recipes = Recipe.objects.filter(user=self.user)

        # Create a recipe serializer allowing more than one items.
        serializer = RecipeSerializer(recipes, many=True)

        # Check that the response code is HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response includes only one recipe.
        self.assertEqual(len(response.data), 1)

        # Check that the data returned is the same as the serializer.
        self.assertEqual(response.data, serializer.data)
