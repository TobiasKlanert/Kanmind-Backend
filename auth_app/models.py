"""
Custom User model.

This module defines a project-specific User model that extends Django's built-in
AbstractUser. It adds a 'fullname' field for display purposes.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Project User model.

    Fields:
    - fullname: optional human-readable full name for the user (max length 150).
      Stored separately from AbstractUser.first_name/last_name to keep a single
      display field.

    Behavior:
    - Inherits all authentication and permission behavior from AbstractUser.
    - No additional methods beyond a readable string representation.
    """
    fullname = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Optional full name used for display purposes."
    )

    def __str__(self):
        """
        Return a human-friendly identifier for the user.

        Preference order:
        1. email (if set)
        2. fullname
        3. fallback to default AbstractUser __str__ if neither is set
        """
        return self.email or self.fullname or super().__str__()
