from src.models import Board
from .base import BaseRepository


class BoardRepository(BaseRepository[Board]):
    def __init__(self):
        super().__init__(Board)
