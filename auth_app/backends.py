"""
Custom authentication backend that allows users to authenticate with an email address
and password instead of the default username-based authentication.
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(BaseBackend):
    """
    Authenticate users using their email and password.

    This backend implements the minimal BaseBackend interface:
    - authenticate(request, email=None, password=None, **kwargs)
      Returns a user instance if credentials are valid, otherwise None.
    - get_user(user_id)
      Returns a user instance for a given primary key or None if not found.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Attempt to authenticate a user using email and password.

        Parameters:
        - email: email credential provided by the caller
        - password: raw password provided by the caller

        Returns:
        - User instance if credentials are valid
        - None if authentication fails or parameters are missing
        """
        # Require both email and password; return early if missing.
        if email is None or password is None:
            return None

        try:
            # Lookup user by email.
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # No user with that email
            return None

        # Verify the password using Django's secure password hashing utilities.
        if user.check_password(password):
            return user

        # Wrong password
        return None

    def get_user(self, user_id):
        """
        Retrieve a user instance by primary key.

        Returns:
        - User instance or None if not found.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
