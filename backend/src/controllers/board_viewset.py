"""
Board ViewSet for Board API endpoints.
Provides CRUD operations for Board resources.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError

from src.serializers.board_serializer import BoardSerializer
from src.services.board_service import BoardService
from src.services.exceptions import NotFoundError, ValidationError


class BoardViewSet(viewsets.ViewSet):
    """
    ViewSet for Board API.
    
    Endpoints:
    - GET /api/boards/ - List all boards (R8)
    - POST /api/boards/ - Create a new board (R9)
    - GET /api/boards/{id}/ - Retrieve a specific board
    - DELETE /api/boards/{id}/ - Delete a board (R14)
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board_service = BoardService()
    
    def _handle_error(self, error: Exception) -> Response:
        """Convert domain exceptions to HTTP responses."""
        if isinstance(error, NotFoundError):
            return Response(
                {
                    "error": "NOT_FOUND",
                    "message": str(error),
                    "field": None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(error, ValidationError):
            return Response(
                {
                    "error": "VALIDATION_FAILED",
                    "message": str(error),
                    "field": error.field
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(error, DRFValidationError):
            # Handle DRF validation errors
            if hasattr(error, 'detail'):
                if isinstance(error.detail, dict):
                    # Field-specific validation error
                    for field, messages in error.detail.items():
                        message = messages[0] if isinstance(messages, list) else str(messages)
                        return Response(
                            {
                                "error": "VALIDATION_FAILED",
                                "message": message,
                                "field": field
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                elif isinstance(error.detail, list):
                    message = error.detail[0]
                    return Response(
                        {
                            "error": "VALIDATION_FAILED",
                            "message": message,
                            "field": None
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {
                    "error": "VALIDATION_FAILED",
                    "message": str(error),
                    "field": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # Unexpected error
            return Response(
                {
                    "error": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                    "field": None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request):
        """
        GET /api/boards/
        List all boards (R8).
        """
        try:
            boards = self.board_service.list_boards()
            serializer = BoardSerializer(boards, many=True)
            return Response(serializer.data)
        except Exception as e:
            return self._handle_error(e)
    
    def create(self, request):
        """
        POST /api/boards/
        Create a new board (R9).
        Validates that name is not empty.
        """
        try:
            serializer = BoardSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            name = serializer.validated_data.get('name')
            board = self.board_service.create_board(name=name)
            
            response_serializer = BoardSerializer(board)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return self._handle_error(e)
    
    def retrieve(self, request, pk=None):
        """
        GET /api/boards/{id}/
        Retrieve a specific board by ID.
        """
        try:
            board = self.board_service.get_board(int(pk))
            serializer = BoardSerializer(board)
            return Response(serializer.data)
        except Exception as e:
            return self._handle_error(e)
    
    def destroy(self, request, pk=None):
        """
        DELETE /api/boards/{id}/
        Delete a board (R14).
        """
        try:
            self.board_service.delete_board(int(pk))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return self._handle_error(e)
