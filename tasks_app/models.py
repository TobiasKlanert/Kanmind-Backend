"""
Task app models.

This module defines the data models for tasks and their comments:
- Task: Represents a task/ticket in a kanban board
- TaskComment: Represents comments associated with tasks

Key features:
- Tasks belong to boards and can be assigned to users
- Tasks have status, priority, and due dates
- Comments track discussion on tasks
"""

from django.db import models
from django.conf import settings
from board_app.models import Board

User = settings.AUTH_USER_MODEL


class Task(models.Model):
    """
    Task model representing a task/ticket in a kanban board.

    Fields:
    - board: ForeignKey to Board (required, CASCADE delete)
    - title: Task title (required)
    - description: Detailed task description (optional)
    - status: Current task state (TODO/IN_PROGRESS/REVIEW/DONE)
    - priority: Task priority level (LOW/MEDIUM/HIGH)
    - assignee: User responsible for task (optional)
    - reviewer: User reviewing the task (optional)
    - due_date: Task deadline (optional)
    - comments_count: Counter for associated comments
    """
    class Status(models.TextChoices):
        """Valid task status values."""
        TODO = "to-do"
        IN_PROGRESS = "in-progress"
        REVIEW = "review"
        DONE = "done"

    class Priority(models.TextChoices):
        """Valid task priority levels."""
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    # Core task fields
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,  # Delete tasks when board is deleted
        related_name="tasks"       # Access via board.tasks
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Task status and priority
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    # Task assignment fields
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # Keep task if user is deleted
        related_name="assigned_tasks",
        null=True,
        blank=True
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # Keep task if reviewer is deleted
        related_name="review_tasks",
        null=True,
        blank=True
    )

    # Task metadata
    due_date = models.DateField(null=True, blank=True)
    comments_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        """
        String representation of a task.
        
        Returns:
            str: Task title and its board name
        """
        return f"{self.title} ({self.board.title})"


class TaskComment(models.Model):
    """
    Model for comments on tasks.

    Fields:
    - task: ForeignKey to Task (required, CASCADE delete)
    - author: ForeignKey to User who wrote comment (required, CASCADE delete)
    - content: Comment text (required)
    - created_at: Timestamp of comment creation
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,  # Delete comments when task is deleted
        related_name="comments",   # Access via task.comments
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Delete comments when user is deleted
        related_name="task_comments",  # Access via user.task_comments
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of a comment.
        
        Returns:
            str: Author name and associated task
        """
        return f"Comment by {self.author} on {self.task}"
