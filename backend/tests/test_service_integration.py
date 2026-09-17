"""Service/repository integration tests against a temporary Django test database."""

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
    assert board.created_at is not None
    assert task.board_id == board.id
    assert task.title == "Build API"
    assert task.description == ""
    assert task.status == TaskStatus.TODO
    assert task.created_at is not None
    assert task.updated_at is not None
    assert tasks.get_task(task.id) == task


def test_list_boards_is_newest_first(services):
    boards, _ = services
    first = boards.create_board("First")
    second = boards.create_board("Second")
    Board.objects.filter(pk=first.id).update(
        created_at=second.created_at - timedelta(days=1)
    )
    assert boards.list_boards() == [second, first]


@pytest.mark.parametrize("status", [None, *TaskStatus.values])
def test_filtering_is_scoped_to_board_and_preserves_creation_order(services, status):
    boards, tasks = services
    board = boards.create_board("Engineering")
    other_board = boards.create_board("Marketing")
    created = []
    start = timezone.now()
    for index, task_status in enumerate(TaskStatus.values * 2):
        task = tasks.create_task(board.id, f"Task {index}", status=task_status)
        Task.objects.filter(pk=task.id).update(
            created_at=start + timedelta(minutes=index)
        )
        created.append(task)
        tasks.create_task(other_board.id, f"Other {index}", status=task_status)

    expected = [
        task.id for task in created if status is None or task.status == status
    ]
    assert [task.id for task in tasks.list_tasks(board.id, status)] == expected


def test_empty_board_and_no_matching_status_return_empty_lists(services):
    boards, tasks = services
    board = boards.create_board("Empty")
    assert tasks.list_tasks(board.id) == []
    tasks.create_task(board.id, "Pending")
    assert tasks.list_tasks(board.id, TaskStatus.DONE) == []


def test_status_update_is_persisted_without_changing_other_fields(services, monkeypatch):
    boards, tasks = services
    board = boards.create_board("Engineering")
    task = tasks.create_task(board.id, "Build API", description="Keep this\ntext")
    created_at = task.created_at
    updated_at = task.updated_at + timedelta(seconds=1)
    monkeypatch.setattr(timezone, "now", lambda: updated_at)

    updated = tasks.update_status(task.id, TaskStatus.DONE)

    updated.refresh_from_db()
    assert updated.status == TaskStatus.DONE
    assert updated.updated_at == updated_at
    assert updated.created_at == created_at
    assert updated.title == "Build API"
    assert updated.description == "Keep this\ntext"
    assert updated.board_id == board.id


def test_invalid_status_update_leaves_persisted_task_unchanged(services):
    boards, tasks = services
    task = tasks.create_task(boards.create_board("Engineering").id, "Task")
    updated_at = task.updated_at

    with pytest.raises(ValidationError):
        tasks.update_status(task.id, "INVALID")

    task.refresh_from_db()
    assert task.status == TaskStatus.TODO
    assert task.updated_at == updated_at


def test_delete_task_preserves_board_and_other_tasks(services):
    boards, tasks = services
    board = boards.create_board("Engineering")
    removed = tasks.create_task(board.id, "Remove")
    retained = tasks.create_task(board.id, "Keep")

    assert tasks.delete_task(removed.id) is None

    assert not Task.objects.filter(pk=removed.id).exists()
    assert boards.get_board(board.id) == board
    assert tasks.list_tasks(board.id) == [retained]
    with pytest.raises(NotFoundError):
        tasks.delete_task(removed.id)


def test_delete_board_uses_orm_cascade_and_preserves_other_boards(services):
    # This verifies Django's delete collector, not a database ON DELETE CASCADE.
    boards, tasks = services
    board = boards.create_board("Remove")
    other_board = boards.create_board("Keep")
    removed_ids = [
        tasks.create_task(board.id, "First").id,
        tasks.create_task(board.id, "Second").id,
    ]
    retained = tasks.create_task(other_board.id, "Keep task")

    assert boards.delete_board(board.id) is None

    assert not Board.objects.filter(pk=board.id).exists()
    assert not Task.objects.filter(pk__in=removed_ids).exists()
    assert boards.get_board(other_board.id) == other_board
    assert tasks.list_tasks(other_board.id) == [retained]
    with pytest.raises(NotFoundError):
        boards.delete_board(board.id)


def test_delete_empty_board(services):
    boards, _ = services
    board = boards.create_board("Empty")
    boards.delete_board(board.id)
    assert not Board.objects.filter(pk=board.id).exists()


@pytest.mark.parametrize(
    "operation",
    [
        "get_board", "delete_board", "list_tasks", "create_task",
        "get_task", "update_status", "delete_task",
    ],
)
def test_missing_resources_through_real_repositories(services, operation):
    boards, tasks = services
    operations = {
        "get_board": lambda: boards.get_board(999),
        "delete_board": lambda: boards.delete_board(999),
        "list_tasks": lambda: tasks.list_tasks(999),
        "create_task": lambda: tasks.create_task(999, "Task"),
        "get_task": lambda: tasks.get_task(999),
        "update_status": lambda: tasks.update_status(999, TaskStatus.DONE),
        "delete_task": lambda: tasks.delete_task(999),
    }
    with pytest.raises(NotFoundError):
        operations[operation]()
    assert not Board.objects.exists()
    assert not Task.objects.exists()
