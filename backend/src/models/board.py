from django.db import models
from .base import BaseModel


class Board(BaseModel):
    """
    Board entity representing a named container for tasks (R1).
    Enforces non-empty name at both application and database level.
    """
    name = models.CharField(
        max_length=255,
        help_text="Name of the board (required, non-empty)"
    )

    class Meta:
        db_table = 'boards'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(name=''),
                name='board_name_not_empty'
            )
        ]

    def __str__(self) -> str:
        return self.name
