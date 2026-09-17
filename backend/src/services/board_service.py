from src.models import Board
from src.repositories.board_repository import BoardRepository
from .exceptions import NotFoundError
from .validation import validate_required_text


class BoardService:
    """Board operations and validation, independent of HTTP."""

    def __init__(self, repository: BoardRepository | None = None):
        self.repository = repository if repository is not None else BoardRepository()

    def list_boards(self) -> list[Board]:
        return self.repository.list_all()

    def get_board(self, board_id: int) -> Board:
        board = self.repository.get_by_id(board_id)
        if board is None:
            raise NotFoundError("Board", board_id)
        return board

    def create_board(self, name: str | None = None) -> Board:
        name = validate_required_text(
            name, "name", Board._meta.get_field("name").max_length
        )
        return self.repository.save(Board(name=name))

    def delete_board(self, board_id: int) -> None:
        board = self.get_board(board_id)
        self.repository.delete(board)
