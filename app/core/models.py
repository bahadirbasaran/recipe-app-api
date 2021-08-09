from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                       PermissionsMixin


class UserManager(BaseUserManager):
    """Class that provides helper functions for creating a user/superuser"""

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""

        if not email:
            raise ValueError('Users should have an e-mail address.')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""

        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True

        # User has been modified after the creation, should be saved again.
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Defines tags to be used in recipes."""

    name = models.CharField(max_length=255)

    # models.CASCADE ensures deletion of the tag when User is deleted.
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Defines the string representation of the model."""

        return self.name


class Ingredient(models.Model):
    """Defines ingredients to be used in recipes."""

    name = models.CharField(max_length=255)

    # models.CASCADE ensures deletion of the ingredient when User is deleted.
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Defines the string representation of the model."""

        return self.name


class Recipe(models.Model):
    """Defines recipe objects."""

    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)

    # Set link as an optional field for recipes.
    link = models.CharField(max_length=255, blank=True)

    # Many ingredients and many tags can be assigned to many recipes.
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')

    # A recipe can be assigned to only one user.
    # models.CASCADE ensures deletion of the tag when User is deleted.
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Defines the string representation of the model."""

        return self.title
