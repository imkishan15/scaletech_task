import base64
from .models import CustomUser
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.core.exceptions import ValidationError
from PIL import Image
from django.utils.timezone import now


def validate_image(image_data):
    """
    Validates that the provided image data is a valid image.

    Args:
        image_data (bytes): The image data in binary format.

    Raises:
        ValidationError: If the image is invalid.
    """
    try:
        image = Image.open(BytesIO(image_data))
        image.verify()
    except Exception as e:
        raise ValidationError("Invalid image.")


class Base64ImageField(serializers.ImageField):
    """
    A custom serializer field to handle Base64-encoded images.

    This field converts a Base64 string into an image file, validates the image,
    and assigns it a unique name based on the current timestamp.
    """

    def to_internal_value(self, data):
        """
        Convert a Base64-encoded string to an image file.

        Args: data (str): The Base64-encoded string representing the image.

        Returns: ContentFile: A Django ContentFile object containing the decoded image.

        Raises: ValidationError: If the Base64 string is invalid or the image cannot be decoded.
        """
        if isinstance(data, str):
            # Check if the string has 'base64,' prefix
            if data.startswith("data:image"):
                # Remove the prefix from the string
                data = data.split("base64,")[-1]
            try:
                # Decode the Base64 string
                decoded_image = base64.b64decode(data)
                # Validate the image
                validate_image(decoded_image)

                image_file = ContentFile(decoded_image)

                # Set the file name (you can modify this to match your needs)
                image_name = f"profile_picture_{now().strftime('%Y%m%d%H%M%S')}.png"  # Example name using timestamp

                # Save the image with the correct name
                image_file.name = image_name
                return image_file
            except Exception as e:
                raise ValidationError("Invalid Base64 image data.")
        return super().to_internal_value(data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Fields:
        - username: The username of the user.
        - email: The email address of the user.
        - password: The password of the user (write-only).

    Methods:
        create(validated_data): Creates a new user instance.
    """

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """
        Creates a new user instance with the provided validated data.

        Args:
            validated_data (dict): The validated data for user creation.

        Returns:
            CustomUser: The created user instance.
        """
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile management.

    Fields:
        - username: The username of the user.
        - email: The email address of the user.
        - bio: A brief biography of the user.
        - phone_number: The phone number of the user.
        - profile_picture: The profile picture of the user (Base64-encoded).

    Notes:
        - The profile_picture field uses the custom Base64ImageField for handling Base64-encoded images.
    """

    profile_picture = Base64ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "bio", "phone_number", "profile_picture"]
