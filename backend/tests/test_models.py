from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from src.models import Board, Task, TaskStatus


class BoardModelTest(TestCase):
    def test_board_empty_name_fails_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Board.objects.create(name="")


class TaskModelTest(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name="Engineering Sprint")

    def test_create_task_with_default_status_todo(self):
        task = Task.objects.create(board=self.board, title="Setup database models")

        self.assertEqual(task.board, self.board)
        self.assertEqual(task.status, TaskStatus.TODO)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)

    def test_task_empty_title_fails_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Task.objects.create(board=self.board, title="")

    def test_task_invalid_status_fails_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Task.objects.create(
                    board=self.board,
                    title="Invalid Status Task",
                    status="INVALID_STATUS",
                )

    def test_task_foreign_key_constraint_enforced_by_database(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Task.objects.create(board_id=999999, title="Task with non-existent board")
                connection.check_constraints()

        self.assertFalse(Task.objects.filter(board_id=999999).exists())
