from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404
from .serializers import TaskSerializer
from ..models import Task
from board_app.models import Board

class CreateTaskView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        board_id = self.request.data.get("board")
        board = get_object_or_404(Board, pk=board_id)
        serializer.save(board=board)

class AssignedTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (Task.objects.filter(assignee=user))
    
class ReviewingTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (Task.objects.filter(reviewer=user))