from django.db import models
from .base import BaseModel
from .board import Board


class TaskStatus(models.TextChoices):
    TODO = 'TODO', 'To Do'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    DONE = 'DONE', 'Done'


class Task(BaseModel):
    """
    Task entity belonging to a board with title, description, and status (R2).
    Enforces real database foreign key, cascade delete, and check constraints (R3, R4).
    """
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks',
        db_index=True,
        db_constraint=True,
        help_text="Board container this task belongs to (R3, R4)"
    )
    title = models.CharField(
        max_length=255,
        help_text="Title of the task (required, non-empty)"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Optional task description"
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
        db_index=True,
        help_text="Current task status (TODO, IN_PROGRESS, DONE)"
    )

    class Meta:
        db_table = 'tasks'
        ordering = ['created_at']
        indexes = [
            # Composite index optimizing GET /api/boards/{boardId}/tasks?status=... (R10)
            models.Index(
                fields=['board', 'status'],
                name='idx_tasks_board_status'
            ),
            # Composite index optimizing board task ordering by created_at
            models.Index(
                fields=['board', 'created_at'],
                name='idx_tasks_board_created'
            ),
        ]
        constraints = [
            # Ensure title cannot be empty string at the database level
            models.CheckConstraint(
                condition=~models.Q(title=''),
                name='task_title_not_empty'
            ),
            # Ensure status is strictly one of the allowed enum choices at the database level
            models.CheckConstraint(
                condition=models.Q(status__in=TaskStatus.values),
                name='task_status_valid'
            ),
        ]

    def __str__(self) -> str:
        return f"[{self.status}] {self.title}"
