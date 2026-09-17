"""Focused unit tests for task business rules, without database or HTTP."""

import pytest

from src.models import Task, TaskStatus
from src.services.exceptions import NotFoundError, ValidationError


def test_create_task_on_existing_board_returns_saved_entity(
    task_service, task_repository, board_repository, board
):
    result = task_service.create_task(board.id, " \tBuild API\n")

    board_repository.get_by_id.assert_called_once_with(board.id)
    task_repository.save.assert_called_once()
    submitted = task_repository.save.call_args.args[0]
    assert result is submitted
    assert isinstance(submitted, Task)
    assert submitted.board_id == board.id
    assert submitted.title == "Build API"
    assert submitted.description == ""
    assert submitted.status == TaskStatus.TODO


@pytest.mark.parametrize(
    ("title", "message"),
    [
        (None, "title is required."),
        ("", "title must not be empty."),
        (" \t\r\n", "title must not be empty."),
        (123, "title must be a string."),
        ("x" * 256, "title must be at most 255 characters."),
    ],
)
def test_create_task_rejects_invalid_title(
    task_service, task_repository, board, title, message
):
    with pytest.raises(ValidationError) as caught:
        task_service.create_task(board.id, title)

    assert caught.value.code == "VALIDATION_FAILED"
    assert caught.value.field == "title"
    assert str(caught.value) == message
    task_repository.save.assert_not_called()


@pytest.mark.parametrize("description", [None, 123])
def test_create_task_rejects_non_string_description(
    task_service, task_repository, board, description
):
    with pytest.raises(ValidationError) as caught:
        task_service.create_task(board.id, "Task", description=description)

    assert caught.value.field == "description"
    assert caught.value.message == "description must be a string."
    task_repository.save.assert_not_called()


@pytest.mark.parametrize(
    ("operation", "status"),
    [
        ("create", "INVALID"),
        ("create", ""),
        ("update", "INVALID"),
        ("update", ""),
        ("filter", "INVALID"),
        ("filter", ""),
    ],
)
def test_invalid_status_is_rejected_without_side_effects(
    task_service, task_repository, task, board, operation, status
):
    with pytest.raises(ValidationError) as caught:
        if operation == "create":
            task_service.create_task(board.id, "Task", status=status)
        elif operation == "update":
            task_service.update_status(task.id, status)
        else:
            task_service.list_tasks(board.id, status=status)

    assert caught.value.code == "VALIDATION_FAILED"
    assert caught.value.field == "status"
    assert caught.value.message == "status must be one of TODO, IN_PROGRESS, DONE."
    assert task.status == TaskStatus.TODO
    task_repository.save.assert_not_called()
    task_repository.list_by_board.assert_not_called()


@pytest.mark.parametrize("operation", ["create", "list"])
def test_missing_board_rejects_task_operation(
    task_service, task_repository, board_repository, operation
):
    board_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError) as caught:
        if operation == "create":
            task_service.create_task(999, "Task")
        else:
            task_service.list_tasks(999)

    assert caught.value.resource == "Board"
    assert caught.value.entity_id == 999
    board_repository.get_by_id.assert_called_once_with(999)
    task_repository.save.assert_not_called()
    task_repository.list_by_board.assert_not_called()


def test_list_tasks_passes_board_and_filter_to_repository(
    task_service, task_repository, board_repository, board, task
):
    task_repository.list_by_board.return_value = [task]

    assert task_service.list_tasks(board.id, status=TaskStatus.DONE) == [task]
    board_repository.get_by_id.assert_called_once_with(board.id)
    task_repository.list_by_board.assert_called_once_with(
        board.id, status=TaskStatus.DONE
    )


def test_update_status_persists_valid_value(task_service, task_repository, task):
    result = task_service.update_status(task.id, TaskStatus.DONE)

    assert result is task
    assert result.status == TaskStatus.DONE
    task_repository.get_by_id.assert_called_once_with(task.id)
    task_repository.save.assert_called_once_with(task)


@pytest.mark.parametrize("operation", ["update", "delete"])
def test_missing_task_raises_domain_error(task_service, task_repository, operation):
    task_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError) as caught:
        if operation == "update":
            task_service.update_status(999, TaskStatus.DONE)
        else:
            task_service.delete_task(999)

    assert caught.value.code == "NOT_FOUND"
    assert caught.value.resource == "Task"
    assert caught.value.entity_id == 999
    task_repository.get_by_id.assert_called_once_with(999)
    task_repository.save.assert_not_called()
    task_repository.delete.assert_not_called()


def test_missing_resource_takes_precedence_over_invalid_input(
    task_service, task_repository, board_repository
):
    board_repository.get_by_id.return_value = None
    task_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError, match="Board"):
        task_service.create_task(999, "")
    with pytest.raises(NotFoundError, match="Board"):
        task_service.list_tasks(999, status="INVALID")
    with pytest.raises(NotFoundError, match="Task"):
        task_service.update_status(999, "INVALID")

    task_repository.save.assert_not_called()
    task_repository.list_by_board.assert_not_called()
