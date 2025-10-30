"""
Task app serializers for REST API endpoints.

This module defines serializers for task-related data:
- UserInlineSerializer: Compact user representation for nested relationships
- TaskSerializer: Main serializer for task CRUD operations
- TaskCommentCreateSerializer: Handles creation of task comments
- TaskCommentResponseSerializer: Formats comment data for responses
"""

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound
from ..models import Task, TaskComment
from board_app.models import Board
from auth_app.models import User


class UserInlineSerializer(serializers.ModelSerializer):
    """
    Compact serializer for User model when nested in other serializers.
    
    Used for assignee and reviewer representations in task data.
    """
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskSerializer(serializers.ModelSerializer):
    """
    Main serializer for Task model handling CRUD operations.

    Fields:
    - Read-only fields: board, comments_count, assignee, reviewer
    - Write-only fields: assignee_id, reviewer_id
    - Regular fields: id, title, description, status, priority, due_date

    Special behavior:
    - Validates user membership in board
    - Handles assignee/reviewer assignments
    - Customizes PATCH response format
    """
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    assignee = UserInlineSerializer(read_only=True)
    reviewer = UserInlineSerializer(read_only=True)

    assignee_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description", "status", "priority",
            "assignee", "reviewer", "assignee_id", "reviewer_id",
            "due_date", "comments_count"
        ]
        read_only_fields = ["board", "comments_count", "assignee", "reviewer"]

    def create(self, validated_data):
        """Create a new task with proper user/board validation."""
        request = self.context.get("request")
        user = getattr(request, "user", None)

        board = validated_data.get("board")
        self._check_user_membership(user, board)

        assignee = self._get_valid_user(validated_data.pop(
            "assignee_id", None), board, "assignee_id")
        reviewer = self._get_valid_user(validated_data.pop(
            "reviewer_id", None), board, "reviewer_id")

        return self._create_task(validated_data, assignee, reviewer)

    def update(self, instance, validated_data):
        """Update existing task with validation checks."""
        request = self.context.get("request")
        user = getattr(request, "user", None)
        board = getattr(instance, "board", None)
        
        assignee_id, reviewer_id = self._pop_user_ids(validated_data)
        self._check_user_membership(user, board)
        
        self._maybe_assign_user(instance, board, assignee_id, "assignee_id", "assignee")
        self._maybe_assign_user(instance, board, reviewer_id, "reviewer_id", "reviewer")
        
        self._update_simple_fields(instance, validated_data)
        instance.save()
        return instance

    # Helper methods for validation and data manipulation
    def _check_user_membership(self, user, board):
        """Verify user is a member/owner of the board."""
        if user is None or not (
            user == board.owner or board.members.filter(pk=user.pk).exists()
        ):
            raise PermissionDenied("User is not a member of this board.")

    def _get_valid_user(self, user_id, board, field_name):
        """Validate and return user for assignment/review."""
        if user_id is None:
            return None
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({field_name: "Invalid user."})

        if not (user == board.owner or board.members.filter(pk=user.pk).exists()):
            raise serializers.ValidationError(
                {field_name: f"{field_name.replace('_id', '').capitalize()} is not a member of this board."}
            )
        return user

    def _create_task(self, validated_data, assignee, reviewer):
        """Create task instance with assigned users."""
        return Task.objects.create(
            assignee=assignee,
            reviewer=reviewer,
            **validated_data,
        )

    def _pop_user_ids(self, data):
        """Extract assignee/reviewer IDs from data."""
        return (
            data.pop("assignee_id", serializers.empty),
            data.pop("reviewer_id", serializers.empty),
        )

    def _maybe_assign_user(self, instance, board, user_id, field_name, attr_name):
        """Conditionally update user assignment if ID provided."""
        if user_id is serializers.empty:
            return
        user = self._get_valid_user(user_id, board, field_name)
        setattr(instance, attr_name, user)

    def _update_simple_fields(self, instance, validated_data):
        """Update basic task fields from validated data."""
        fields = ["title", "description", "status", "priority", "due_date"]
        for field in fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

    def to_representation(self, instance):
        """Customize data representation for responses."""
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and request.method == "PATCH":
            data.pop("board", None)
            data.pop("comments_count", None)
        return data


class TaskCommentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new task comments.
    
    Fields:
    - content: The text content of the comment
    """
    content = serializers.CharField()


class TaskCommentResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for formatting task comment responses.
    
    Fields:
    - id: Comment ID
    - created_at: Timestamp
    - author: Author's fullname or username
    - content: Comment text
    """
    author = serializers.SerializerMethodField()

    class Meta:
        model = TaskComment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        """Return author's fullname or username as fallback."""
        return getattr(obj.author, "fullname", None) or getattr(obj.author, "username", "")
