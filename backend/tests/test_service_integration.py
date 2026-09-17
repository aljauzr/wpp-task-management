"""Focused service/repository integration tests against a test database."""

from datetime import timedelta

import pytest
from django.utils import timezone

from src.models import Board, Task, TaskStatus
from src.services import BoardService, TaskService
from src.services.exceptions import NotFoundError, ValidationError


pytestmark = pytest.mark.django_db


@pytest.fixture
def services():
    boards = BoardService()
    return boards, TaskService(board_service=boards)


def test_services_persist_board_and_task_with_defaults(services):
    boards, tasks = services
    board = boards.create_board("  Engineering  ")
    task = tasks.create_task(board.id, "  Build API  ")

    board.refresh_from_db()
    task.refresh_from_db()
    assert board.name == "Engineering"
    assert task.board_id == board.id
    assert task.title == "Build API"
    assert task.description == ""
    assert task.status == TaskStatus.TODO


@pytest.mark.parametrize("status", [None, TaskStatus.DONE])
def test_filtering_is_scoped_to_board_and_preserves_creation_order(services, status):
    boards, tasks = services
    board = boards.create_board("Engineering")
    other_board = boards.create_board("Marketing")
    start = timezone.now()

    first = tasks.create_task(board.id, "First", status=TaskStatus.TODO)
    Task.objects.filter(pk=first.id).update(created_at=start)
    second = tasks.create_task(board.id, "Second", status=TaskStatus.DONE)
    Task.objects.filter(pk=second.id).update(created_at=start + timedelta(minutes=1))
    tasks.create_task(other_board.id, "Other", status=TaskStatus.DONE)

    expected = [first.id, second.id] if status is None else [second.id]
    assert [task.id for task in tasks.list_tasks(board.id, status)] == expected


def test_invalid_status_update_leaves_persisted_task_unchanged(services):
    boards, tasks = services
    task = tasks.create_task(boards.create_board("Engineering").id, "Task")
    updated_at = task.updated_at

    with pytest.raises(ValidationError):
        tasks.update_status(task.id, "INVALID")

    task.refresh_from_db()
    assert task.status == TaskStatus.TODO
    assert task.updated_at == updated_at


def test_delete_board_uses_orm_cascade_and_preserves_other_boards(services):
    boards, tasks = services
    board = boards.create_board("Remove")
    other_board = boards.create_board("Keep")
    removed_task = tasks.create_task(board.id, "First")
    kept_task = tasks.create_task(other_board.id, "Keep task")

    assert boards.delete_board(board.id) is None

    assert not Board.objects.filter(pk=board.id).exists()
    assert not Task.objects.filter(pk=removed_task.id).exists()
    assert boards.get_board(other_board.id) == other_board
    assert tasks.list_tasks(other_board.id) == [kept_task]


@pytest.mark.parametrize(
    "operation",
    ["create_task", "update_status", "delete_task"],
)
def test_missing_resources_through_real_repositories(services, operation):
    boards, tasks = services
    operations = {
        "create_task": lambda: tasks.create_task(999, "Task"),
        "update_status": lambda: tasks.update_status(999, TaskStatus.DONE),
        "delete_task": lambda: tasks.delete_task(999),
    }

    with pytest.raises(NotFoundError):
        operations[operation]()

    assert not Board.objects.exists()
    assert not Task.objects.exists()
