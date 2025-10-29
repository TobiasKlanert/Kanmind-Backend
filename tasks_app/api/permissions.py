from rest_framework import permissions


class IsReviewerOrBoardOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            obj.reviewer == user or
            obj.board.owner == user
        )
