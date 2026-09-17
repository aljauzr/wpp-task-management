from django.test import TestCase
from django.db import IntegrityError, transaction, connection
from src.models import Board, Task, TaskStatus


class BoardModelTest(TestCase):
    """
    Tests for Board database schema, defaults, and constraints (R1, R5).
    """

    def test_create_board_successfully(self):
        board = Board.objects.create(name="Q3 Website Refresh")
        self.assertIsNotNone(board.id)
        self.assertEqual(board.name, "Q3 Website Refresh")
        self.assertIsNotNone(board.created_at)
        self.assertIsNotNone(board.updated_at)
        self.assertEqual(str(board), "Q3 Website Refresh")

    def test_board_empty_name_fails_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Board.objects.create(name="")


class TaskModelTest(TestCase):
    """
    Tests for Task database schema, relationships, and constraints (R2, R3, R4, R5).
    """

    def setUp(self):
        self.board = Board.objects.create(name="Engineering Sprint")

    def test_create_task_with_default_status_todo(self):
        task = Task.objects.create(
            board=self.board,
            title="Setup database models",
            description="Create Board and Task models with constraints"
        )
        self.assertIsNotNone(task.id)
        self.assertEqual(task.board, self.board)
        self.assertEqual(task.status, TaskStatus.TODO)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
        self.assertEqual(str(task), "[TODO] Setup database models")

    def test_create_task_with_explicit_status(self):
        task = Task.objects.create(
            board=self.board,
            title="Active Task",
            status=TaskStatus.IN_PROGRESS
        )
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)

    def test_cascade_delete_board_removes_tasks(self):
        """
        R4 requirement: Enforce delete behavior at schema level.
        Deleting a board automatically removes all associated tasks via ON DELETE CASCADE.
        """
        task1 = Task.objects.create(board=self.board, title="Task 1")
        task2 = Task.objects.create(board=self.board, title="Task 2")

        task1_id = task1.id
        task2_id = task2.id

        # Delete board
        self.board.delete()

        # Both tasks must be deleted from database
        self.assertFalse(Task.objects.filter(id=task1_id).exists())
        self.assertFalse(Task.objects.filter(id=task2_id).exists())

    def test_task_empty_title_fails_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Task.objects.create(board=self.board, title="")

    def test_task_invalid_status_fails_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Task.objects.create(board=self.board, title="Invalid Status Task", status="INVALID_STATUS")

    def test_task_foreign_key_constraint_enforced_by_database(self):
        """
        R3 requirement: Foreign key constraint enforced by the database itself.
        A task must not be able to reference a board that does not exist.
        """
        Task.objects.create(board_id=999999, title="Task with non-existent board")
        try:
            with self.assertRaises(IntegrityError):
                connection.check_constraints()
        finally:
            Task.objects.filter(board_id=999999).delete()
