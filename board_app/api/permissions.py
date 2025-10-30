"""
Custom permissions for the board app API.

This module defines permission classes that control access to board-related views.
"""

from rest_framework import permissions


class IsOwnerOrMember(permissions.BasePermission):
    """
    Custom permission to only allow owners or members of a board to access it.

    Behavior:
    - Allows access if the requesting user is the board owner
    - Allows access if the requesting user is in the board's members
    - Denies access in all other cases
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access this board object.

        Args:
            request: The incoming request
            view: The view being accessed
            obj: The board instance being accessed

        Returns:
            bool: True if user is owner or member, False otherwise
        """
        # Owner always has full access
        if obj.owner == request.user:
            return True

        # Members have access too
        if request.user in obj.members.all():
            return True

        # Everyone else is denied access
        return False
