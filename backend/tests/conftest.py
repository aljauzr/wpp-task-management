from unittest.mock import create_autospec

import pytest

from src.models import Board, Task
from src.repositories import BoardRepository, TaskRepository
from src.services import BoardService, TaskService


@pytest.fixture
def board():
    return Board(id=1, name="Engineering")


@pytest.fixture
def task(board):
    return Task(id=10, board=board, title="Write tests")


@pytest.fixture
def board_repository(board):
    repository = create_autospec(BoardRepository, instance=True, spec_set=True)
    repository.get_by_id.return_value = board
    repository.save.side_effect = lambda entity: entity
    return repository


@pytest.fixture
def task_repository(task):
    repository = create_autospec(TaskRepository, instance=True, spec_set=True)
    repository.get_by_id.return_value = task
    repository.save.side_effect = lambda entity: entity
    return repository


@pytest.fixture
def board_service(board_repository):
    return BoardService(repository=board_repository)


@pytest.fixture
def task_service(task_repository, board_service):
    return TaskService(repository=task_repository, board_service=board_service)
