from rest_framework import generics, permissions
from .serializers import BoardSerializer
from ..models import Board


class BoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (Board.objects.filter(owner=user) | Board.objects.filter(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save()
