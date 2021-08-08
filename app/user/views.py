from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """User creation view that points to the serializer
    class that are used to create the object."""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """New authentication token creation view."""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Authenticated user management view."""

    serializer_class = UserSerializer

    # Set the permission level users have. The only permission allowed
    # here is that users must be authenticated to use the API.
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Overridden to return the user that has been authenticated.
        When it is called, request will have the user attached to it
        because of the authentication_classes."""

        return self.request.user
