from django.db.models import F
from rest_framework import generics, permissions, mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .serializers import TaskSerializer, TaskCommentCreateSerializer, TaskCommentResponseSerializer
from .permissions import IsBoardMemberForUpdateOrReviewerOrOwnerForDelete, IsBoardMemberOfTask
from ..models import Task, TaskComment
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
    permission_classes = [permissions.IsAuthenticated,
                          IsBoardMemberForUpdateOrReviewerOrOwnerForDelete]
    queryset = Task.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class TaskCommentView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsBoardMemberOfTask]
    serializer_class = TaskCommentCreateSerializer

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        self.check_object_permissions(request, task)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = TaskComment.objects.create(
            task=task,
            author=request.user,
            content=serializer.validated_data["content"],
        )

        Task.objects.filter(pk=task.pk).update(
            comments_count=F("comments_count") + 1)

        response_data = TaskCommentResponseSerializer(comment).data
        return Response(response_data, status=status.HTTP_201_CREATED)
