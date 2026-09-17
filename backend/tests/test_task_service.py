"""Unit tests for business rules, with no database or HTTP client."""

import pytest

from src.models import Task, TaskStatus
from src.services.exceptions import NotFoundError, ValidationError


def test_create_task_on_existing_board_returns_saved_entity(
    task_service, task_repository, board_repository, board
):
    saved_task = Task(id=42, board=board, title="Build API")
    task_repository.save.side_effect = None
    task_repository.save.return_value = saved_task

    result = task_service.create_task(
        board.id, " \tBuild API\n", description="  Keep formatting\n\nDetails  "
    )

    assert result is saved_task
    board_repository.get_by_id.assert_called_once_with(board.id)
    task_repository.save.assert_called_once()
    submitted = task_repository.save.call_args.args[0]
    assert isinstance(submitted, Task)
    assert submitted.board_id == board.id
    assert submitted.title == "Build API"
    assert submitted.description == "  Keep formatting\n\nDetails  "
    assert submitted.status == TaskStatus.TODO


def test_create_task_defaults_to_empty_description_and_todo(task_service, board):
    result = task_service.create_task(board.id, "Write tests")
    assert result.description == ""
    assert result.status == TaskStatus.TODO


@pytest.mark.parametrize("status", TaskStatus.values)
def test_create_task_accepts_each_status(task_service, board, status):
    assert task_service.create_task(board.id, "Task", status=status).status == status


@pytest.mark.parametrize(
    ("title", "message"),
    [
        (None, "title is required."),
        ("", "title must not be empty."),
        (" \t\r\n", "title must not be empty."),
        (123, "title must be a string."),
        (False, "title must be a string."),
        ([], "title must be a string."),
        ({}, "title must be a string."),
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


def test_create_task_rejects_missing_title(task_service, task_repository, board):
    with pytest.raises(ValidationError, match="title is required"):
        task_service.create_task(board.id)
    task_repository.save.assert_not_called()


def test_create_task_accepts_maximum_title_length_after_trimming(task_service, board):
    result = task_service.create_task(board.id, " " + "x" * 255 + "\n")
    assert result.title == "x" * 255


@pytest.mark.parametrize("description", [None, 123, False, [], {}])
def test_create_task_rejects_non_string_description(
    task_service, task_repository, board, description
):
    with pytest.raises(ValidationError) as caught:
        task_service.create_task(board.id, "Task", description=description)

    assert caught.value.field == "description"
    assert caught.value.message == "description must be a string."
    task_repository.save.assert_not_called()


@pytest.mark.parametrize("operation", ["create", "update", "filter"])
@pytest.mark.parametrize("status", ["INVALID", "", "todo", " DONE ", 123, False, [], {}])
def test_invalid_status_is_rejected_without_writing_or_listing_tasks(
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


def test_create_task_rejects_explicit_null_status(task_service, task_repository, board):
    with pytest.raises(ValidationError, match="status must be one of"):
        task_service.create_task(board.id, "Task", status=None)
    task_repository.save.assert_not_called()


def test_update_status_requires_a_value(task_service, task_repository, task):
    with pytest.raises(ValidationError, match="status must be one of"):
        task_service.update_status(task.id)
    assert task.status == TaskStatus.TODO
    task_repository.save.assert_not_called()


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


@pytest.mark.parametrize("status", [None, *TaskStatus.values])
def test_list_tasks_passes_board_and_filter_to_repository(
    task_service, task_repository, board_repository, board, task, status
):
    task_repository.list_by_board.return_value = [task]

    assert task_service.list_tasks(board.id, status=status) == [task]
    board_repository.get_by_id.assert_called_once_with(board.id)
    task_repository.list_by_board.assert_called_once_with(board.id, status=status)


def test_list_tasks_for_empty_board_returns_empty_list(
    task_service, task_repository, board
):
    task_repository.list_by_board.return_value = []
    assert task_service.list_tasks(board.id) == []


@pytest.mark.parametrize("status", TaskStatus.values)
def test_update_status_accepts_all_values_including_current_status(
    task_service, task_repository, task, status
):
    result = task_service.update_status(task.id, status)
    assert result is task
    assert result.status == status
    task_repository.get_by_id.assert_called_once_with(task.id)
    task_repository.save.assert_called_once_with(task)


def test_get_task_returns_existing_task(task_service, task_repository, task):
    assert task_service.get_task(task.id) is task
    task_repository.get_by_id.assert_called_once_with(task.id)


@pytest.mark.parametrize("operation", ["get", "update", "delete"])
def test_missing_task_raises_domain_error(task_service, task_repository, operation):
    task_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError) as caught:
        if operation == "get":
            task_service.get_task(999)
        elif operation == "update":
            task_service.update_status(999, TaskStatus.DONE)
        else:
            task_service.delete_task(999)

    assert caught.value.code == "NOT_FOUND"
    assert caught.value.resource == "Task"
    assert caught.value.entity_id == 999
    assert str(caught.value) == "Task with id 999 was not found."
    task_repository.get_by_id.assert_called_once_with(999)
    task_repository.save.assert_not_called()
    task_repository.delete.assert_not_called()


def test_delete_task_delegates_to_repository(task_service, task_repository, task):
    assert task_service.delete_task(task.id) is None
    task_repository.delete.assert_called_once_with(task)


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
