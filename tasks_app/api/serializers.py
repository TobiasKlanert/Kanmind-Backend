from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound
from ..models import Task
from board_app.models import Board
from auth_app.models import User


class UserInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskSerializer(serializers.ModelSerializer):
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
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "assignee_id",
            "reviewer_id",
            "due_date",
            "comments_count"
        ]
        read_only_fields = ["board", "comments_count", "assignee", "reviewer"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        board = validated_data.get("board")
        self._check_user_membership(user, board)

        assignee = self._get_valid_user(validated_data.pop(
            "assignee_id", None), board, "assignee_id")
        reviewer = self._get_valid_user(validated_data.pop(
            "reviewer_id", None), board, "reviewer_id")

        return self._create_task(validated_data, assignee, reviewer)

    def _check_user_membership(self, user, board):
        if user is None or not (
            user == board.owner or board.members.filter(pk=user.pk).exists()
        ):
            raise PermissionDenied("User is not a member of this board.")

    def _get_valid_user(self, user_id, board, field_name):
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
        return Task.objects.create(
            assignee=assignee,
            reviewer=reviewer,
            **validated_data,
        )
