from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer
from .serializers import UserRegistrationSerializer, UserProfileSerializer

User = get_user_model()


class UserRegistrationView(APIView):
    """
    View for registering new users.

    This view allows new users to create an account by providing the required details,
    such as email, username, and password. Upon successful registration, the user
    is saved to the database, and a success response is returned.

    Methods:
        post(request, *args, **kwargs):
            Handles the POST request to register a new user.
            - Validates the provided data using the UserRegistrationSerializer.
            - Creates a new user if the data is valid.
            - Returns a success response or validation errors.
    """

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Custom login view for authenticating users using email and password.

    This view allows users to log in by providing their email and password. Upon successful
    authentication, it returns a pair of JWT tokens (access and refresh) for the user.

    Methods:
        post(request, *args, **kwargs):
            Handles the POST request to authenticate a user.
            - Validates the email and password.
            - Returns JWT tokens if the credentials are valid.
            - Returns an error response if the credentials are invalid.
    """

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
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
