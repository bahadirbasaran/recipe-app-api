import os
import tempfile

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


URL_RECIPES = reverse('recipe:recipe-list')


def get_image_upload_url(recipe_id):
    """Helper function to return recipe image upload URL."""

    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def get_detail_url(recipe_id):
    """Helper function to return recipe detail URL."""

    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_sample_tag(user, name='Main Course'):
    """Helper function to create and return a sample tag."""

    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name='Cinnamon'):
    """Helper function to create and return a sample ingredient."""

    return Ingredient.objects.create(user=user, name=name)


def create_sample_recipe(user, **parameters):
    """Helper function to create and return a sample recipe."""

    default_parameters = {
        'title': 'Test Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    # Override the parameters or create new ones based on optionals parameters.
    default_parameters.update(parameters)

    return Recipe.objects.create(user=user, **default_parameters)


class PublicRecipeAPITests(TestCase):
    """Tests for unauthenticated recipe API accesses."""

    def setUp(self):
        """The setUp method is run before every test."""

        self.client = APIClient()

    def test_auth_required(self):
        """Tests that authentication is required for retrieving recipes."""

        # Retrieve the recipes belonging to user.
        response = self.client.get(URL_RECIPES)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Tests for authenticated recipe API accesses."""

    def setUp(self):
        """The setUp method is run before every test."""

        credentials = {'email': 'testuser@gmail.com', 'password': 'Testpass12'}
        self.user = get_user_model().objects.create_user(**credentials)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Tests retrieving a list of recipes."""

        # Create two sample recipes.
        create_sample_recipe(user=self.user)
        create_sample_recipe(user=self.user)

        # Retrieve the recipes belonging to user.
        response = self.client.get(URL_RECIPES)

        # Retrieve recipes from the database.
        # Ensure ingredients are returned in reverse order based on the ID.
        recipes = Recipe.objects.all().order_by('-id')

        # Create a recipe serializer allowing more than one items.
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_authenticated_user(self):
        """Tests that retrieved recipes are limited to authenticated users."""

        # Create a new user in addition to the user created in
        # the setUp, and leave it without an authentication.
        credentials = {'email': 'newuser@gmail.com', 'password': 'Testpass34'}
        new_user = get_user_model().objects.create_user(**credentials)

        # Create a sample recipe that is assigned to the new user.
        create_sample_recipe(user=new_user)

        # Create a sample recipe that is assigned to the authenticated user.
        create_sample_recipe(user=self.user)

        response = self.client.get(URL_RECIPES)

        # Filter the recipes with the authenticated user.
        recipes = Recipe.objects.filter(user=self.user)

        # Create a recipe serializer allowing more than one items.
        serializer = RecipeSerializer(recipes, many=True)

        # Check that the response is HTTP 200, and includes only 1 recipe.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Check that the data returned is the same as the serializer.
        self.assertEqual(response.data, serializer.data)

    def test_view_recipe_detail(self):
        """Tests viewing a recipe detail."""

        recipe = create_sample_recipe(user=self.user)
        tag = create_sample_tag(user=self.user)
        ingredient = create_sample_ingredient(user=self.user)
        recipe.tags.add(tag)
        recipe.ingredients.add(ingredient)

        url = get_detail_url(recipe_id=recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        """Tests new recipe creation."""

        recipe_payload = {
            'title': 'Chocolate Cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }
        response = self.client.post(URL_RECIPES, recipe_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the created recipe from the models.
        recipe = Recipe.objects.get(id=response.data['id'])

        # Check that the correct values have been assigned to the recipe.
        for key in recipe_payload.keys():
            self.assertEqual(recipe_payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Tests new recipe creation with tags."""

        # Create sample tags.
        tag1 = create_sample_tag(user=self.user, name='Vegan')
        tag2 = create_sample_tag(user=self.user, name='Dessert')

        # Create a sample recipe by assigning the created sample tags.
        recipe_payload = {
            'title': 'Avocado Lime Cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        response = self.client.post(URL_RECIPES, recipe_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the created recipe and tags created with the recipe.
        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()

        # Check that 2 tags were created, and they were the correct ones.
        self.assertEqual(len(tags), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Tests new recipe creation with ingredients."""

        # Create sample ingredients.
        ingredient1 = create_sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = create_sample_ingredient(user=self.user, name='Curry')

        # Create a sample recipe by assigning the created sample ingredients.
        recipe_payload = {
            'title': 'Thai Prawn with Curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 7.00
        }
        response = self.client.post(URL_RECIPES, recipe_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the created recipe and ingredients created with the recipe.
        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()

        # Check that 2 ingredients were created and they were the correct ones.
        self.assertEqual(len(ingredients), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Tests partially updating a recipe with patch."""

        recipe = create_sample_recipe(user=self.user)
        tag = create_sample_tag(user=self.user)
        recipe.tags.add(tag)

        new_tag = create_sample_tag(user=self.user, name='Curry')

        recipe_payload = {'title': 'Chicken Tikka', 'tags': [new_tag.id]}

        # Use the detail URL to update an object.
        url = get_detail_url(recipe_id=recipe.id)

        # Update the recipe partially using patch.
        self.client.patch(url, recipe_payload)

        # Refresh the details of the recipe from the database.
        recipe.refresh_from_db()

        # Check that the update was successful.
        self.assertEqual(recipe.title, recipe_payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Tests fully updating a recipe with put."""

        recipe = create_sample_recipe(user=self.user)
        tag = create_sample_tag(user=self.user)
        recipe.tags.add(tag)

        recipe_payload = {
            'title': 'Spaghetti Bolognese',
            'time_minutes': 25,
            'price': 5
        }

        # Use the detail URL to update an object.
        url = get_detail_url(recipe_id=recipe.id)

        # Update the recipe fully using put.
        self.client.put(url, recipe_payload)

        # Refresh the details of the recipe from the database.
        recipe.refresh_from_db()

        # Check that the update was successful.
        self.assertEqual(recipe.title, recipe_payload['title'])
        self.assertEqual(recipe.time_minutes, recipe_payload['time_minutes'])
        self.assertEqual(recipe.price, recipe_payload['price'])

        # Check that the tags assigned equals to 0, since HTTP PUT clears a
        # field if the field is omitted (there is no tag in recipe_payload).
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadAPITests(TestCase):
    """Tests for recipe image upload API accesses."""

    def setUp(self):
        """The setUp method is run before every test."""

        credentials = {'email': 'testuser@gmail.com', 'password': 'Testpass12'}
        self.user = get_user_model().objects.create_user(**credentials)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.recipe = create_sample_recipe(user=self.user)

    def tearDown(self):
        """The tearDown method is run after every test."""

        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Tests uploading image to recipes."""

        url = get_image_upload_url(self.recipe.id)

        # Create a named temporary file.
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new(mode='RGB', size=(10, 10))
            img.save(fp=ntf, format='JPEG')

            # Set the file pointer to the beginning of the image.
            ntf.seek(0)

            response = self.client.post(
                url,
                {'image': ntf},
                format='multipart'
            )

        # Refresh the details of the recipe from the database.
        self.recipe.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_to_recipe_bad_request(self):
        """Tests uploading invalid image to recipes."""

        url = get_image_upload_url(self.recipe.id)

        # Pass a string instead of an image.
        response = self.client.post(url, {'image': 'img'}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """Tests filtering recipes by specific tags."""

        # Create sample recipes.
        recipe1 = create_sample_recipe(user=self.user, title='Thai Curry')
        recipe2 = create_sample_recipe(user=self.user, title='Lime Cheesecake')
        recipe3 = create_sample_recipe(user=self.user, title='Fish and Chips')

        # Create sample tags.
        tag1 = create_sample_tag(user=self.user, name='Vegan')
        tag2 = create_sample_tag(user=self.user, name='Dessert')

        # Add the tags onto the recipes.
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        # The response should only include the first two recipes.
        response = self.client.get(
            URL_RECIPES,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_recipes_by_ingredients(self):
        """Tests filtering recipes by specific ingredients."""

        # Create sample recipes.
        recipe1 = create_sample_recipe(user=self.user, title='Pasta Bolognese')
        recipe2 = create_sample_recipe(user=self.user, title='Kiwi Cheesecake')
        recipe3 = create_sample_recipe(user=self.user, title='Steak&Mushrooms')

        # Create sample ingredients.
        ingredient1 = create_sample_ingredient(user=self.user, name='Tomato')
        ingredient2 = create_sample_ingredient(user=self.user, name='Kiwi')

        # Add the ingredients to the recipes.
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        # The response should only include the first two recipes.
        response = self.client.get(
            URL_RECIPES,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)
