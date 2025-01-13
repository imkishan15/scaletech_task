from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Fields:
        - bio (TextField): An optional field for the user's biography.
        - phone_number (CharField): An optional field for the user's phone number, with a maximum length of 15.
        - profile_picture (ImageField): An optional field for the user's profile picture,
          stored in the 'profile_pictures/' directory.

    Methods:
        - __str__: Returns the username of the user as a string representation.
    """

    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )

    def __str__(self):
        """
        Returns the string representation of the user, which is the username.

        Returns:
            str: The username of the user.
        """
        return self.username
