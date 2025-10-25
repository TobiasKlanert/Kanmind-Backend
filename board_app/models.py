from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Board(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_boards"
    )
    members = models.ManyToManyField(
        User,
        related_name="boards",
        blank=True
    )

    def __str__(self):
        return self.title

    @property
    def member_count(self):
        return self.members.count()

    @property
    def ticket_count(self):
        return self.tasks.count()

    @property
    def tasks_to_do_count(self):
        return self.tasks.filter(status="todo").count()

    @property
    def tasks_high_prio_count(self):
        return self.tasks.filter(priority="high").count()
