from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


URL_TAGS = reverse('recipe:tag-list')


class PublicTagsAPITests(TestCase):
    """Tests for unauthenticated Tag API accesses."""

    def setUp(self):
        """The setUp method is run before every test."""

        self.client = APIClient()

    def test_login_required_to_retrieve_tags(self):
        """Tests that login is required for retrieving tags."""

        response = self.client.get(URL_TAGS)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Tests for authenticated Tag API accesses."""

    def setUp(self):
        """The setUp method is run before every test."""

        credentials = {'email': 'testuser@gmail.com', 'password': 'Testpass12'}
        self.user = get_user_model().objects.create_user(**credentials)

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Tests retrieving tags."""

        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # Retrieve the tags belonging to the authenticated user.
        response = self.client.get(URL_TAGS)

        # Retrieve tags from the database.
        # Ensure tags are returned in reverse order based on the name.
        tags = Tag.objects.all().order_by('-name')

        # Create a tag serializer allowing more than one item.
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_authenticated_user(self):
        """Tests that retrieved tags are limited to authenticated users."""

        # Create a new user in addition to the user created in
        # the setUp, and leave it without an authentication.
        credentials = {'email': 'newuser@gmail.com', 'password': 'Testpass34'}
        new_user = get_user_model().objects.create_user(**credentials)

        # Create a tag that is assigned to the new user.
        Tag.objects.create(user=new_user, name='Fruity')

        # Create a tag that is assigned to the authenticated user.
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        response = self.client.get(URL_TAGS)

        # Check that the response is HTTP 200, and includes only one tag.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Check that the name of the returned tag matches with the
        # name of the tag that was assigned to the authenticated user.
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tag(self):
        """Tests a new tag creation."""

        tag_payload = {'name': 'Test Tag'}
        self.client.post(URL_TAGS, tag_payload)

        is_tag_created = Tag.objects.filter(
            user=self.user,
            name=tag_payload['name']
        ).exists()

        self.assertTrue(is_tag_created)

    def test_create_tag_invalid_payload(self):
        """Tests creating a new tag with invalid payload."""

        tag_payload = {'name': ''}
        response = self.client.post(URL_TAGS, tag_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Tests filtering tags by those assigned to recipes."""

        # Create two tags, assign one of them to a recipe
        # while leaving the other one unassigned.
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')

        recipe = Recipe.objects.create(
            title='Turkish Omlette with Minced Meat',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe.tags.add(tag1)

        response = self.client.get(URL_TAGS, {'assigned_only': True})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        # The response only includes the tag1.
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_tags_assigned_unique(self):
        """Tests filtering tags by assigned returns unique items."""

        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')

        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=3.00,
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=1.00,
            user=self.user
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        response = self.client.get(URL_TAGS, {'assigned_only': True})

        self.assertEqual(len(response.data), 1)
