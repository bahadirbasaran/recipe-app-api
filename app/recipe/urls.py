from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views


# DefaultRouter automatically registers appropriate
# URLs for all actions in ViewSet
router = DefaultRouter()

# Register the TagViewSet with the router
router.register('tags', views.TagViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
