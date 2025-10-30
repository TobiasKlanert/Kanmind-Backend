"""
Custom permissions for the tasks app API.

This module defines permission classes that control access to task-related views:
- IsBoardMemberForUpdateOrReviewerOrOwnerForDelete: Controls task modification rights
- IsBoardMemberOfTask: Ensures user is member of the board the task belongs to
- IsAuthorOfTaskComment: Restricts comment modifications to the author
"""

from rest_framework import permissions
from ..models import Task, TaskComment


class IsBoardMemberForUpdateOrReviewerOrOwnerForDelete(permissions.BasePermission):
    """
    Permission class for task modifications.

    Rules:
    - PATCH/PUT: User must be a board member or owner
    - DELETE: User must be the task reviewer or board owner
    - Other methods: User must be authenticated

    This ensures that:
    - Only board members can update tasks
    - Only reviewers or board owners can delete tasks
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_member = (user == obj.board.owner) or obj.board.members.filter(
            pk=user.pk).exists()

        # For updates (PATCH/PUT), require board membership
        if request.method in ("PATCH", "PUT"):
            return is_member

        # For deletions, require reviewer or board owner status
        if request.method == "DELETE":
            return (obj.reviewer == user) or (obj.board.owner == user)

        # Default: allow if authenticated
        return request.user and request.user.is_authenticated


class IsBoardMemberOfTask(permissions.BasePermission):
    """
    Permission class to ensure user is a member of the task's board.

    Rules:
    - Object must be a Task instance
    - User must be either:
      - The board owner
      - A member of the board

    Used to restrict task access to board members only.
    """

    def has_object_permission(self, request, view, obj):
        # Verify object type
        if not isinstance(obj, Task):
            return False
        
        user = request.user
        board = obj.board
        return (user == board.owner) or board.members.filter(pk=user.pk).exists()


class IsAuthorOfTaskComment(permissions.BasePermission):
    """
    Permission class to restrict comment modifications to the author.

    Rules:
    - Object must be a TaskComment instance
    - User must be the original author of the comment

    Used to ensure only comment authors can modify their comments.
    """

    def has_object_permission(self, request, view, obj):
        # Verify object type
        if not isinstance(obj, TaskComment):
            return False
        
        return obj.author_id == request.user.id
