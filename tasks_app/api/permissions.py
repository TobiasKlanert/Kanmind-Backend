from rest_framework import permissions
from ..models import Task, TaskComment


class IsBoardMemberForUpdateOrReviewerOrOwnerForDelete(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_member = (user == obj.board.owner) or obj.board.members.filter(
            pk=user.pk).exists()

        if request.method in ("PATCH", "PUT"):
            return is_member

        if request.method == "DELETE":
            return (obj.reviewer == user) or (obj.board.owner == user)

        return request.user and request.user.is_authenticated


class IsBoardMemberOfTask(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Task):
            return False
        user = request.user
        board = obj.board
        return (user == board.owner) or board.members.filter(pk=user.pk).exists()


class IsAuthorOfTaskComment(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, TaskComment):
            return False
        return obj.author_id == request.user.id
