from src.models import Task, TaskStatus
from src.repositories.task_repository import TaskRepository
from .board_service import BoardService
from .exceptions import NotFoundError
from .validation import (
    validate_description,
    validate_required_text,
    validate_status,
)


class TaskService:
    """Task business rules; persistence is delegated to repositories."""

    def __init__(
        self,
        repository: TaskRepository | None = None,
        board_service: BoardService | None = None,
    ):
        self.repository = repository if repository is not None else TaskRepository()
        self.board_service = (
            board_service if board_service is not None else BoardService()
        )

    def get_task(self, task_id: int) -> Task:
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task", task_id)
        return task

    def list_tasks(self, board_id: int, status: str | None = None) -> list[Task]:
        self.board_service.get_board(board_id)
        if status is not None:
            status = validate_status(status)
        return self.repository.list_by_board(board_id, status=status)

    def create_task(
        self,
        board_id: int,
        title: str | None = None,
        description: str = "",
        status: str = TaskStatus.TODO,
    ) -> Task:
        board = self.board_service.get_board(board_id)
        title = validate_required_text(
            title, "title", Task._meta.get_field("title").max_length
        )
        description = validate_description(description)
        status = validate_status(status)
        return self.repository.save(
            Task(board=board, title=title, description=description, status=status)
        )

    def update_status(self, task_id: int, status: str | None = None) -> Task:
        task = self.get_task(task_id)
        status = validate_status(status)
        task.status = status
        return self.repository.save(task)

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.repository.delete(task)
