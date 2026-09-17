"""Regression tests for direct SQL behavior around FK and cascade rules."""

import pytest
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from src.models import Board, Task


pytestmark = pytest.mark.django_db(transaction=True)


def test_direct_sql_delete_cascades_only_to_the_selected_boards_tasks():
    board = Board.objects.create(name="Delete")
    other_board = Board.objects.create(name="Keep")
    removed = Task.objects.create(board=board, title="Task to remove")
    retained = Task.objects.create(board=other_board, title="Keep task")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM boards WHERE id = %s", [board.id])

    assert not Board.objects.filter(pk=board.id).exists()
    assert not Task.objects.filter(pk=removed.id).exists()
    assert Board.objects.filter(pk=other_board.id).exists()
    assert Task.objects.filter(pk=retained.id, board_id=other_board.id).exists()
    connection.check_constraints()


def test_direct_sql_cascade_is_rolled_back_with_the_parent_delete():
    board = Board.objects.create(name="Keep after rollback")
    task = Task.objects.create(board=board, title="Keep task")

    with pytest.raises(RuntimeError, match="Cancel deletion"):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM boards WHERE id = %s", [board.id])
            assert not Task.objects.filter(pk=task.id).exists()
            raise RuntimeError("Cancel deletion")

    assert Board.objects.filter(pk=board.id).exists()
    assert Task.objects.filter(pk=task.id, board_id=board.id).exists()
    connection.check_constraints()


def test_direct_sql_insert_still_rejects_a_nonexistent_board():
    now = timezone.now()

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tasks "
                    "(board_id, title, description, status, created_at, updated_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    [999999, "Orphan", "", "TODO", now, now],
                )

    assert not Task.objects.exists()
