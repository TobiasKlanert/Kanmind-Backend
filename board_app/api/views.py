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
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (Board.objects.filter(owner=user) | Board.objects.filter(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save()

class BoardDetailView(generics.RetrieveAPIView, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()

        data = request.data.copy()
        members_ids = data.pop("members", None)

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if members_ids is not None:
            if not isinstance(members_ids, (list, tuple)):
                return Response({"detail": "members must be a list of IDs"}, status=400)
            users = User.objects.filter(id__in=members_ids)
            if users.count() != len(set(members_ids)):
                return Response({"detail": "one or more member IDs are invalid"}, status=400)
            instance.members.set(users)

        owner_data = UserInlineSerializer(instance.owner).data
        members_data = UserInlineSerializer(instance.members.all(), many=True).data

        return Response({
            "id": instance.id,
            "title": instance.title,
            "owner_data": owner_data,
            "members_data": members_data,
        })
