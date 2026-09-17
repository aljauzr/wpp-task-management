from src.models import Task
from .base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self):
        super().__init__(Task)

    def list_by_board(self, board_id: int, status: str | None = None) -> list[Task]:
        tasks = self.model.objects.filter(board_id=board_id)
        if status is not None:
            tasks = tasks.filter(status=status)
        return list(tasks)
