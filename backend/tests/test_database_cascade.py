"""R3/R4 regression tests that bypass Django's deletion collector."""

import pytest
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from src.models import Board, Task, TaskStatus


pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.parametrize("task_count", [0, 1, 3])
def test_direct_sql_delete_cascades_only_to_the_selected_boards_tasks(task_count):
    board = Board.objects.create(name="Delete")
    other_board = Board.objects.create(name="Keep")
    for index in range(task_count):
        Task.objects.create(
            board=board, title=f"Task {index}", status=TaskStatus.values[index]
        )
    retained = Task.objects.create(board=other_board, title="Keep task")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM boards WHERE id = %s", [board.id])

    assert not Board.objects.filter(pk=board.id).exists()
    assert not Task.objects.filter(board_id=board.id).exists()
    assert Board.objects.get(pk=other_board.id).name == "Keep"
    assert list(Task.objects.values_list("id", flat=True)) == [retained.id]
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


def test_direct_sql_update_still_rejects_a_nonexistent_board():
    board = Board.objects.create(name="Keep")
    task = Task.objects.create(board=board, title="Keep task")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE tasks SET board_id = %s WHERE id = %s",
                    [999999, task.id],
                )

    task.refresh_from_db()
    assert task.board_id == board.id
