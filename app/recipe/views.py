from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from recipe import serializers


class RecipeAttributesViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin):
    """Base ViewSet for user owned recipe attributes."""

    authentication_classes = (TokenAuthentication,)

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Overrides the get_queryset function to return objects
        (ordered by name) for authenticated users only."""

        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Overrides the default creation to set user to authenticated user."""

        serializer.save(user=self.request.user)


class TagViewSet(RecipeAttributesViewSet):
    """Manages tags in the database."""

    queryset = Tag.objects.all()

    serializer_class = serializers.TagSerializer


class IngredientViewSet(RecipeAttributesViewSet):
    """Manages ingredients in the database."""

    queryset = Ingredient.objects.all()

    serializer_class = serializers.IngredientSerializer
