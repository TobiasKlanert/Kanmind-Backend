from rest_framework import generics, permissions
from .serializers import BoardSerializer, BoardDetailSerializer
from .permissions import IsOwnerOrMember
from ..models import Board


class BoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (Board.objects.filter(owner=user) | Board.objects.filter(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save()

class BoardDetailView(generics.RetrieveAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]
