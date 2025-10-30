"""
Board app models.

This module defines the Board model which represents a kanban board in the application.
Boards have an owner and can have multiple members who can access them.
"""

from django.db import models
from django.conf import settings

# Get the user model specified in settings.AUTH_USER_MODEL
User = settings.AUTH_USER_MODEL


class Board(models.Model):
    """
    Board model representing a kanban board.

    Fields:
    - title: The name/title of the board (required)
    - owner: ForeignKey to User model, represents board creator/owner
    - members: ManyToManyField to User model, represents users with access

    Relationships:
    - owner: One-to-many (User can own multiple boards)
    - members: Many-to-many (Users can be members of multiple boards,
              boards can have multiple members)

    Note:
    - When owner is deleted, all their boards are deleted (CASCADE)
    - members field can be blank (boards can exist without members)
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Delete board when owner is deleted
        related_name="owned_boards"  # Access via user.owned_boards
    )
    members = models.ManyToManyField(
        User,
        related_name="boards",  # Access via user.boards
        blank=True  # Board can exist without members
    )

    def __str__(self):
        """
        String representation of the Board model.
        
        Returns:
            str: The board's title
        """
        return self.title