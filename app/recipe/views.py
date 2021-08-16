from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class RecipeAttributesViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin):
    """Base ViewSet for user owned recipe attributes."""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Overrides the get_queryset function to return objects
        (ordered by name) for authenticated users only.
        """
        assigned_only = self.request.query_params.get('assigned_only', False)
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

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


class RecipeViewSet(viewsets.ModelViewSet):
    """Manages recipes in the database."""

    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, str_IDs):
        """Converts a list of string IDs to a list of integers."""

        return [int(str_ID) for str_ID in str_IDs.split(',')]

    def get_queryset(self):
        """Overrides the get_queryset function to return
        objects for authenticated users only."""

        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_IDs = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_IDs)

        if ingredients:
            ingredient_IDs = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_IDs)

        return queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Returs an appropriate serializer class."""

        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Overrides the default creation to set user to authenticated user."""

        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Uploads an image to a recipe."""

        # Get the object that is being accessed based on the ID in the URL.
        recipe = self.get_object()

        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
