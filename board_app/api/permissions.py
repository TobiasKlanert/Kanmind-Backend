from rest_framework import permissions


class IsOwnerOrMember(permissions.BasePermission):
    """
    Custom permission: Only the owner or a member of the board can access it.
    """

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        if request.user in obj.members.all():
            return True
        return False
