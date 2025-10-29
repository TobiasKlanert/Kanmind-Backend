from rest_framework import permissions


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
