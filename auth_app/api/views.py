"""
API views for authentication-related endpoints.

This module exposes three class-based views:
- RegistrationView: allow anonymous users to register. Returns auth token and basic user info.
- CustomLoginView: allow anonymous users to log in using email + password. Returns auth token and user info.
- EmailCheckView: authenticated-only endpoint to check whether an email is registered and return basic user info.
"""
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer, EmailAuthTokenSerializer
from ..models import User


class RegistrationView(APIView):
    """
    POST /registration/

    Permissions: AllowAny (anonymous users may create accounts)

    Request body: handled by RegistrationSerializer (fullname, email, password, repeated_password)

    Success response (201):
    {
        "token": "<auth token>",
        "fullname": "<username/fullname>",
        "email": "<email>",
        "user_id": <id>
    }

    Error response (400): serializer validation errors.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Validate incoming registration data
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            # Create user and a token for authentication
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)

            data = {
                'token': token.key,
                'fullname': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id
            }
            return Response(data, status=status.HTTP_201_CREATED)

        # Return serializer errors for invalid input
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(APIView):
    """
    POST /login/

    Permissions: AllowAny

    Request body: { "email": "...", "password": "..." } validated by EmailAuthTokenSerializer.

    Behavior:
    - Uses the serializer to authenticate (serializer adds 'user' to validated_data).
    - Returns or creates a Token for the authenticated user and returns basic user info.

    Success response (200):
    {
        "token": "<auth token>",
        "fullname": "<fullname>",
        "email": "<email>",
        "user_id": <id>
    }

    Errors:
    - 400 with serializer errors if credentials missing/invalid.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Validate credentials and authenticate via serializer
        serializer = EmailAuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        data = {
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id
        }
        return Response(data)


class EmailCheckView(APIView):
    """
    GET /email-check/?email=<email>

    Permissions: IsAuthenticated (only authenticated users may call this endpoint)

    Query params:
    - email (required): the email address to check.

    Behavior:
    - Validates the email format using DRF's EmailField.
    - Returns 404 if no user found with the provided email.
    - Returns 200 with basic user info if a user exists.

    Example success response (200):
    {
        "id": <user id>,
        "email": "<email>",
        "fullname": "<fullname>"
    }

    Errors:
    - 400 if 'email' query parameter is missing or invalid.
    - 404 if email is not found.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve 'email' from query parameters
        email = request.query_params.get('email')
        if not email:
            return Response({'email': ['This query parameter is required.']}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format using DRF serializer field utilities
        try:
            email = serializers.EmailField().to_internal_value(email)
        except serializers.ValidationError as e:
            return Response({'email': e.detail}, status=status.HTTP_400_BAD_REQUEST)

        # Case-insensitive lookup for a user with this email
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Return limited public information about the matched user
        data = {
            'id': user.id,
            'email': user.email,
            'fullname': user.fullname,
        }
        return Response(data, status=status.HTTP_200_OK)
