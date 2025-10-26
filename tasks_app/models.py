from django.db import models
from django.conf import settings
from board_app.models import Board

User = settings.AUTH_USER_MODEL


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "to-do"
        IN_PROGRESS = "in-progress"
        REVIEW = "review"
        DONE = "done"

    class Priority(models.TextChoices):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
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
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="review_tasks",
        null=True,
        blank=True
    )
    due_date = models.DateField(null=True, blank=True)
    comments_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.board.title})"
