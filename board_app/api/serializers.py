from rest_framework import serializers
from ..models import Board
from auth_app.models import User
from tasks_app.models import Task


class BoardSerializer(serializers.ModelSerializer):
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
        members = validated_data.pop("members", [])
        user = self.context["request"].user
        board = Board.objects.create(owner=user, **validated_data)
        board.members.set(members)
        return board

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return getattr(obj, "tasks", []).count() if hasattr(obj, "tasks") else 0

    def get_tasks_to_do_count(self, obj):
        if hasattr(obj, "tasks"):
            return obj.tasks.filter(status="TODO").count()
        return 0

    def get_tasks_high_prio_count(self, obj):
        if hasattr(obj, "tasks"):
            return obj.tasks.filter(priority="HIGH").count()
        return 0


class UserInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskInlineSerializer(serializers.ModelSerializer):
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
        return getattr(obj, "comments", []).count() if hasattr(obj, "comments") else 0


class BoardDetailSerializer(serializers.ModelSerializer):
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
