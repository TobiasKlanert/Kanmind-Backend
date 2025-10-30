"""
Board app API views.

This module provides the view classes that handle board-related API endpoints:
- BoardListCreateView: List and create boards
- BoardDetailView: Retrieve, update, and delete specific boards

These views use DRF's generic views and mixins for common REST operations.
"""

from rest_framework import generics, permissions, mixins
from rest_framework.response import Response
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    UserInlineSerializer,
)
from .permissions import IsOwnerOrMember
from auth_app.models import User
from ..models import Board


class BoardListCreateView(generics.ListCreateAPIView):
    """
    API view to list and create boards.

    GET: Returns a list of boards the authenticated user has access to
         (either as owner or member)
    POST: Creates a new board with the authenticated user as owner

    Permissions:
    - Requires authentication
    """
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get the list of boards accessible to the current user.
        
        Returns boards where the user is either:
        - The owner of the board
        - A member of the board
        
        Uses distinct() to avoid duplicate entries if user is both owner and member.
        """
        user = self.request.user
        return (Board.objects.filter(owner=user) | 
                Board.objects.filter(members=user)).distinct()

    def perform_create(self, serializer):
        """Create a new board instance."""
        serializer.save()


class BoardDetailView(generics.RetrieveAPIView, 
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin):
    """
    API view for retrieving, updating and deleting specific boards.

    GET: Returns detailed information about a specific board
    PATCH: Updates board details (title and/or members)
    DELETE: Removes the board

    Permissions:
    - Requires authentication
    - User must be either owner or member of the board
    """
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]

    def delete(self, request, *args, **kwargs):
        """Handle DELETE requests to remove a board."""
        return self.destroy(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests to update board details.

        Supports updating:
        - Board title
        - Board members (expects a list of user IDs)

        Returns:
        - Updated board data including owner and member details

        Raises:
        - 400 Bad Request if members data is invalid
        """
        instance = self.get_object()

        # Separate member updates from other field updates
        data = request.data.copy()
        members_ids = data.pop("members", None)

        # Update non-member fields
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Handle member updates if provided
        if members_ids is not None:
            # Validate members data format
            if not isinstance(members_ids, (list, tuple)):
                return Response(
                    {"detail": "members must be a list of IDs"}, 
                    status=400
                )
            
            # Validate all member IDs exist
            users = User.objects.filter(id__in=members_ids)
            if users.count() != len(set(members_ids)):
                return Response(
                    {"detail": "one or more member IDs are invalid"}, 
                    status=400
                )
            
            # Update board members
            instance.members.set(users)

        # Prepare detailed response including related data
        owner_data = UserInlineSerializer(instance.owner).data
        members_data = UserInlineSerializer(
            instance.members.all(), 
            many=True
        ).data

        return Response({
            "id": instance.id,
            "title": instance.title,
            "owner_data": owner_data,
            "members_data": members_data,
        })
