from rest_framework import generics, permissions, mixins
from rest_framework.generics import get_object_or_404
from .serializers import TaskSerializer
from .permissions import IsBoardMemberForUpdateOrReviewerOrOwnerForDelete
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
    
class TaskDetailView(mixins.UpdateModelMixin, generics.DestroyAPIView, mixins.DestroyModelMixin):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardMemberForUpdateOrReviewerOrOwnerForDelete]
    queryset = Task.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
