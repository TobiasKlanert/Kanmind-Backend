"""
Board app serializers for REST API endpoints.

This module defines serializers for board-related data:
- BoardSerializer: Basic board representation with computed statistics
- BoardDetailSerializer: Detailed board view with related data
- UserInlineSerializer: Compact user representation for nested relationships
- TaskInlineSerializer: Task representation for use within board details
"""

from rest_framework import serializers
from ..models import Board
from auth_app.models import User
from tasks_app.models import Task


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board model with computed statistics.

    Fields:
    - Standard fields: id, title
    - Computed fields: member_count, ticket_count, tasks_to_do_count, tasks_high_prio_count
    - Relations: members (write-only), owner_id (read-only)
    """
    member_count = serializers.SerializerMethodField(read_only=True)
    ticket_count = serializers.SerializerMethodField(read_only=True)
    tasks_to_do_count = serializers.SerializerMethodField(read_only=True)
    tasks_high_prio_count = serializers.SerializerMethodField(read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def create(self, validated_data):
        """
        Create a new board instance.
        
        Sets the requesting user as owner and handles the many-to-many
        relationship for board members.
        """
        members = validated_data.pop("members", [])
        user = self.context["request"].user
        board = Board.objects.create(owner=user, **validated_data)
        board.members.set(members)
        return board

    def get_member_count(self, obj):
        """Count of members associated with this board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Total count of tasks (tickets) on this board."""
        return getattr(obj, "tasks", []).count() if hasattr(obj, "tasks") else 0

    def get_tasks_to_do_count(self, obj):
        """Count of tasks with 'TODO' status."""
        if hasattr(obj, "tasks"):
            return obj.tasks.filter(status="TODO").count()
        return 0

    def get_tasks_high_prio_count(self, obj):
        """Count of tasks with 'HIGH' priority."""
        if hasattr(obj, "tasks"):
            return obj.tasks.filter(priority="HIGH").count()
        return 0


class UserInlineSerializer(serializers.ModelSerializer):
    """
    Compact serializer for User model when nested in other serializers.
    
    Only includes essential user information for display purposes.
    """
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskInlineSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model when included in board details.
    
    Includes nested user information for assignee and reviewer,
    plus a computed comment count.
    """
    assignee = UserInlineSerializer(read_only=True)
    reviewer = UserInlineSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """Count of comments associated with this task."""
        return getattr(obj, "comments", []).count() if hasattr(obj, "comments") else 0


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Detailed board serializer including related data.
    
    Used for detailed views where full information about members
    and tasks is needed. Includes nested serializers for related data.
    """
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserInlineSerializer(many=True, read_only=True)
    tasks = TaskInlineSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]
