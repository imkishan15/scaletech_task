from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserProfileSerializer


class RegisterUserView(APIView):
    """
    API view for user registration.

    Methods:
        post: Handles the registration of a new user. Validates the input data
              and creates a new user if valid.

    Request Body:
        - username: (str) The desired username for the user.
        - email: (str) The email address of the user.
        - password: (str) The password for the user.
    """

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    API view for retrieving and updating the authenticated user's profile.

    Permissions:
        - Requires the user to be authenticated.

    Methods:
        get: Retrieves the profile details of the authenticated user.
        put: Updates the profile details of the authenticated user. Supports
             partial updates.

    Request Body (PUT):
        - bio: (str) A short bio about the user.
        - phone_number: (str) The user's phone number.
        - profile_picture: (file) An optional profile picture for the user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves the profile details of the authenticated user.
        """
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """
        Updates the profile details of the authenticated user.

        Partial updates are supported, meaning only the fields provided in the
        request body will be updated.
        """
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
