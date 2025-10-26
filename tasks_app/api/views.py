from rest_framework import generics, permissions
from .serializers import TaskSerializer
from ..models import Task

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