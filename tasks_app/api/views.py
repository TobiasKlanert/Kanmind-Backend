"""
Task app API views.

This module provides view classes for task-related operations:
- Task creation and management
- Task assignment and review handling
- Task comment functionality

All views require authentication and implement specific permission checks.
"""

from django.db.models import F
from rest_framework import generics, permissions, mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .serializers import TaskSerializer, TaskCommentCreateSerializer, TaskCommentResponseSerializer
from .permissions import (
    IsBoardMemberForUpdateOrReviewerOrOwnerForDelete,
    IsBoardMemberOfTask,
    IsAuthorOfTaskComment,
)
from ..models import Task, TaskComment
from board_app.models import Board


class CreateTaskView(generics.CreateAPIView):
    """
    API endpoint for creating new tasks.

    POST /api/tasks/
    Requires:
    - Authentication
    - Valid board ID in request data
    - Board membership for the authenticated user
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Create task and associate it with specified board."""
        board_id = self.request.data.get("board")
        board = get_object_or_404(Board, pk=board_id)
        serializer.save(board=board)


class AssignedTaskListView(generics.ListAPIView):
    """
    API endpoint to list tasks assigned to the current user.

    GET /api/tasks/assigned-to-me/
    Returns all tasks where the authenticated user is the assignee.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter tasks where current user is assignee."""
        user = self.request.user
        return Task.objects.filter(assignee=user)


class ReviewingTaskListView(generics.ListAPIView):
    """
    API endpoint to list tasks where current user is reviewer.

    GET /api/tasks/reviewing/
    Returns all tasks where the authenticated user is set as reviewer.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter tasks where current user is reviewer."""
        user = self.request.user
        return Task.objects.filter(reviewer=user)


class TaskDetailView(mixins.UpdateModelMixin, 
                    generics.DestroyAPIView,
                    mixins.DestroyModelMixin):
    """
    API endpoint for task detail operations.

    PATCH /api/tasks/<pk>/
    - Update task details (requires board membership)
    
    DELETE /api/tasks/<pk>/
    - Delete task (requires reviewer or board owner status)
    """
    serializer_class = TaskSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsBoardMemberForUpdateOrReviewerOrOwnerForDelete
    ]
    queryset = Task.objects.all()

    def delete(self, request, *args, **kwargs):
        """Handle DELETE requests for task removal."""
        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Handle PATCH requests for task updates."""
        return self.partial_update(request, *args, **kwargs)


class TaskCommentView(generics.GenericAPIView):
    """
    API endpoint for task comments list and creation.

    GET /api/tasks/<pk>/comments/
    - List all comments for a task

    POST /api/tasks/<pk>/comments/
    - Add new comment to task
    - Automatically increments task's comment count
    """
    permission_classes = [permissions.IsAuthenticated, IsBoardMemberOfTask]
    serializer_class = TaskCommentCreateSerializer

    def get(self, request, pk):
        """List all comments for specified task."""
        task = get_object_or_404(Task, pk=pk)
        self.check_object_permissions(request, task)
        comments = TaskComment.objects.filter(task=task).order_by("created_at")
        data = TaskCommentResponseSerializer(comments, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        """Create new comment for specified task."""
        task = get_object_or_404(Task, pk=pk)
        self.check_object_permissions(request, task)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create comment and associate with task and author
        comment = TaskComment.objects.create(
            task=task,
            author=request.user,
            content=serializer.validated_data["content"],
        )

        # Increment comment count atomically
        Task.objects.filter(pk=task.pk).update(
            comments_count=F("comments_count") + 1)

        response_data = TaskCommentResponseSerializer(comment).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class TaskCommentDetailView(generics.DestroyAPIView):
    """
    API endpoint for comment detail operations.

    DELETE /api/tasks/<pk>/comments/<comment_pk>/
    - Delete specific comment
    - Requires comment author status
    - Automatically decrements task's comment count
    """
    permission_classes = [permissions.IsAuthenticated, IsAuthorOfTaskComment]
    queryset = TaskComment.objects.all()
    lookup_url_kwarg = "comment_pk"

    def get_object(self):
        """Retrieve comment ensuring it belongs to specified task."""
        task = get_object_or_404(Task, pk=self.kwargs.get("pk"))
        comment = get_object_or_404(
            TaskComment,
            pk=self.kwargs.get("comment_pk"),
            task=task
        )
        self.check_object_permissions(self.request, comment)
        return comment

    def perform_destroy(self, instance):
        """Delete comment and update task's comment count."""
        task_id = instance.task_id
        instance.delete()
        Task.objects.filter(pk=task_id).update(
            comments_count=F("comments_count") - 1
        )
