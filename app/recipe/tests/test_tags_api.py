from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


URL_TAGS = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Tests for unauthenticated Tag API accesses."""

    def setUp(self):
        """SetUp function is run before every test."""

        self.client = APIClient()

    def test_login_required_to_retrieve_tags(self):
        """Tests that login is required for retrieving tags."""

        response = self.client.get(URL_TAGS)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Tests for authenticated Tag API accesses."""

    def setUp(self):
        """SetUp function is run before every test."""

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
        # Ensure tags are returned in reversed order based on name.
        tags = Tag.objects.all().order_by('-name')

        # Create a tag serializer allowing more than one items.
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_authenticated_user(self):
        """Tests that retrieved tags are limited to authenticated users."""

        # Create a new user addition to the user created in
        # setup, and leave it without an authentication.
        credentials = {'email': 'newuser@gmail.com', 'password': 'Testpass34'}
        new_user = get_user_model().objects.create_user(**credentials)

        # Create a tag that is assigned to the new user.
        Tag.objects.create(user=new_user, name='Fruity')

        # Create a tag that is assigned to the authenticated user.
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        response = self.client.get(URL_TAGS)

        # Check that the response code is HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response includes only one tag.
        self.assertEqual(len(response.data), 1)

        # Check that the name of the returned tag matches with the
        # name of the tag that was assigned to the authenticated user.
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tag(self):
        """Tests new tag creation."""

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
