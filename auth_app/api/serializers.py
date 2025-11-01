"""
Serializers for the authentication API.

This module defines:
- RegistrationSerializer: validates registration data and creates a new User.
- EmailAuthTokenSerializer: validates email/password credentials for authentication.

"""

from django.contrib.auth import authenticate
from rest_framework import serializers
from ..models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Fields:
    - fullname: displayed full name (also used as username here)
    - email: user's email address (unique)
    - password: write-only password
    - repeated_password: write-only confirmation password

    Behavior:
    - Validates that password and repeated_password match.
    - Ensures the email is not already registered.
    - Creates a User instance, hashes the password with set_password, and saves it.
    """
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def save(self):
        """
        Create and return a new User from validated_data.

        Raises:
            serializers.ValidationError: if passwords don't match or email already exists.

        Returns:
            User: newly created user instance.
        """
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        # Ensure the two password entries match
        if pw != repeated_pw:
            raise serializers.ValidationError(
                {'error': 'passwords dont match'})

        # Ensure email uniqueness
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({
                "email": "Email already exists"
            })

        # Create new user; use fullname as username field here
        account = User(
            email=self.validated_data['email'],
            username=self.validated_data['fullname'],
            fullname=self.validated_data['fullname']
        )

        # Hash and set password, then persist
        account.set_password(pw)
        account.save()
        return account


class EmailAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for email-based authentication (token obtain).

    Fields:
    - email: EmailField
    - password: write-only CharField

    validate():
    - Uses django.contrib.auth.authenticate(...) with email and password.
    - Expects an authentication backend that supports email authentication.
    - On success, stores the authenticated user in attrs['user'].
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validate email and password and authenticate the user.

        Raises:
            serializers.ValidationError: if credentials are missing or invalid.

        Returns:
            dict: attrs augmented with 'user' key for the authenticated user.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        # Both fields required
        if email and password:
            # authenticate need a custom backend that accepts 'email' (./backends.py)
            user = authenticate(request=self.context.get(
                'request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError(
                "Must include 'email' and 'password'.")

        # Attach the authenticated user for use by the view
        attrs['user'] = user
        return attrs
