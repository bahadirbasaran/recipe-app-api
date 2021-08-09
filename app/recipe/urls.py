from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views


# DefaultRouter automatically registers appropriate
# URLs for all actions in ViewSet.
router = DefaultRouter()

# Register the view sets with the router.
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
