"""Unit tests: pytest-django blocks database access in this module."""

import pytest

from src.models import Board
from src.services.exceptions import NotFoundError, ValidationError


def test_create_board_trims_name_and_returns_saved_entity(
    board_service, board_repository
):
    saved_board = Board(id=42, name="Q3 Website Refresh")
    board_repository.save.side_effect = None
    board_repository.save.return_value = saved_board

    result = board_service.create_board(" \tQ3 Website Refresh\n")

    assert result is saved_board
    board_repository.save.assert_called_once()
    submitted = board_repository.save.call_args.args[0]
    assert isinstance(submitted, Board)
    assert submitted.name == "Q3 Website Refresh"


@pytest.mark.parametrize(
    ("name", "message"),
    [
        (None, "name is required."),
        ("", "name must not be empty."),
        (" \t\r\n", "name must not be empty."),
        (123, "name must be a string."),
        (False, "name must be a string."),
        ([], "name must be a string."),
        ({}, "name must be a string."),
        ("x" * 256, "name must be at most 255 characters."),
    ],
)
def test_create_board_rejects_invalid_name(
    board_service, board_repository, name, message
):
    with pytest.raises(ValidationError) as caught:
        board_service.create_board(name)

    assert caught.value.code == "VALIDATION_FAILED"
    assert caught.value.field == "name"
    assert str(caught.value) == message
    board_repository.save.assert_not_called()


def test_create_board_rejects_missing_name(board_service, board_repository):
    with pytest.raises(ValidationError, match="name is required"):
        board_service.create_board()
    board_repository.save.assert_not_called()


def test_create_board_accepts_maximum_length_after_trimming(board_service):
    board = board_service.create_board("  " + "x" * 255 + "\n")
    assert board.name == "x" * 255


def test_list_boards_returns_repository_results(board_service, board_repository, board):
    board_repository.list_all.return_value = [board]

    assert board_service.list_boards() == [board]
    board_repository.list_all.assert_called_once_with()


def test_list_boards_returns_empty_list(board_service, board_repository):
    board_repository.list_all.return_value = []
    assert board_service.list_boards() == []


def test_get_board_returns_existing_board(board_service, board_repository, board):
    assert board_service.get_board(board.id) is board
    board_repository.get_by_id.assert_called_once_with(board.id)


@pytest.mark.parametrize("operation", ["get_board", "delete_board"])
def test_missing_board_raises_domain_error(board_service, board_repository, operation):
    board_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError) as caught:
        getattr(board_service, operation)(999)

    assert caught.value.code == "NOT_FOUND"
    assert caught.value.resource == "Board"
    assert caught.value.entity_id == 999
    assert caught.value.field is None
    assert str(caught.value) == "Board with id 999 was not found."
    board_repository.get_by_id.assert_called_once_with(999)
    board_repository.delete.assert_not_called()


def test_delete_board_delegates_to_repository(board_service, board_repository, board):
    assert board_service.delete_board(board.id) is None
    board_repository.delete.assert_called_once_with(board)
