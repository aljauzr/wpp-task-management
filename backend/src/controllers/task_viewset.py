"""
Task ViewSet for Task API endpoints.
Provides CRUD operations for Task resources with custom board-scoped actions.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError

from src.serializers.task_serializer import TaskSerializer
from src.services.task_service import TaskService
from src.services.exceptions import NotFoundError, ValidationError


class TaskViewSet(viewsets.ViewSet):
    """
    ViewSet for Task API.
    
    Endpoints:
    - GET /api/boards/{board_id}/tasks/?status= - List tasks by board (R10)
    - POST /api/boards/{board_id}/tasks/ - Create task on board (R11)
    - PATCH /api/tasks/{id}/ - Partial update task (R12)
    - DELETE /api/tasks/{id}/ - Delete task (R13)
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_service = TaskService()
    
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
    
    @action(detail=False, methods=['get'], url_path='boards/(?P<board_id>[^/.]+)/tasks')
    def list_tasks_by_board(self, request, board_id=None):
        """
        GET /api/boards/{board_id}/tasks/?status=
        List all tasks for a specific board, optionally filtered by status (R10).
        """
        try:
            status_filter = request.query_params.get('status', None)
            tasks = self.task_service.list_tasks(
                board_id=int(board_id),
                status=status_filter
            )
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        except Exception as e:
            return self._handle_error(e)
    
    @action(detail=False, methods=['post'], url_path='boards/(?P<board_id>[^/.]+)/tasks')
    def create_task_on_board(self, request, board_id=None):
        """
        POST /api/boards/{board_id}/tasks/
        Create a new task on a specific board (R11).
        """
        try:
            serializer = TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            title = serializer.validated_data.get('title')
            description = serializer.validated_data.get('description', '')
            status = serializer.validated_data.get('status', 'TODO')
            
            task = self.task_service.create_task(
                board_id=int(board_id),
                title=title,
                description=description,
                status=status
            )
            
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return self._handle_error(e)
    
    def partial_update(self, request, pk=None):
        """
        PATCH /api/tasks/{id}/
        Partially update a task (R12) - currently supports status update.
        """
        try:
            # Only status updates are supported for now
            status_value = request.data.get('status')
            
            task = self.task_service.update_status(
                task_id=int(pk),
                status=status_value
            )
            
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except Exception as e:
            return self._handle_error(e)
    
    def destroy(self, request, pk=None):
        """
        DELETE /api/tasks/{id}/
        Delete a task (R13).
        """
        try:
            self.task_service.delete_task(int(pk))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return self._handle_error(e)
