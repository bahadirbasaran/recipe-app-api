from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects."""

    class Meta:
        """Serializer metadata."""

        # Base model.
        model = get_user_model()

        # Fields to be included in serializer. These are the fields that are
        # accepted during user creation and will be accessible in the API
        # to read/write. They are converted to/from JSON during a HTTP POST.
        fields = ('email', 'password', 'name')

        # Extra args to ensure write-only and min. 5 characters-long passwords.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Creates a new user with an encrypted password and returns it.
        Overridden to use the create_user in the User model to ensure passwords
        to be encrypted. validated_data is a JSON from an HTTP POST"""

        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Updates a user by setting the password correctly, and returns it."""

        # Remove and retrieve password from validated_data. The default value
        # is set to None, since setting a password is optional in this design.
        password = validated_data.pop('password', None)

        user = super().update(instance, validated_data)

        # If user has provided a password, set the password and save the user.
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object."""

    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, credentials):
        """Validate and authenticate users."""

        user = authenticate(
            request=self.context.get('request'),
            username=credentials.get('email'),
            password=credentials.get('password')
        )
        if not user:
            msg = _('Unable to authenticate with the provided credentials.')
            raise serializers.ValidationError(msg, code='authentication')

        credentials['user'] = user

        return credentials
