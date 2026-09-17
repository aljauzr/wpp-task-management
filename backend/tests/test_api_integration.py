"""
Comprehensive API Integration Tests for REST Endpoints.

Tests all Board and Task API endpoints including:
- Board CRUD operations
- Task CRUD operations within boards
- Error response formats
- Edge cases and validation
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Board, Task, TaskStatus


@pytest.fixture
def api_client():
    """Return an APIClient instance."""
    return APIClient()


@pytest.fixture
def create_board():
    """Factory fixture to create a board."""
    def _create_board(name="Test Board"):
        return Board.objects.create(name=name)
    return _create_board


@pytest.fixture
def create_task(create_board):
    """Factory fixture to create a task."""
    def _create_task(board=None, title="Test Task", description="", status=TaskStatus.TODO):
        if board is None:
            board = create_board()
        return Task.objects.create(
            board=board,
            title=title,
            description=description,
            status=status
        )
    return _create_task


def _get_board_id_from_response(response):
    """Helper to extract board ID from a response or object."""
    if hasattr(response, 'id'):
        return response.id
    if isinstance(response, dict):
        return response.get('id')
    return response


@pytest.mark.django_db
class TestBoardListAPI:
    """Tests for GET /api/boards/ - List all boards."""

    def test_list_empty_boards(self, api_client):
        """Should return empty list when no boards exist."""
        response = api_client.get('/api/boards/')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_with_boards(self, api_client, create_board):
        """Should return list of boards ordered by created_at desc."""
        import time
        
        board1 = create_board(name="First Board")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        board2 = create_board(name="Second Board")
        time.sleep(0.01)
        board3 = create_board(name="Third Board")

        response = api_client.get('/api/boards/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        # Should be ordered by created_at desc (newest first)
        assert data[0]['name'] == "Third Board"
        assert data[1]['name'] == "Second Board"
        assert data[2]['name'] == "First Board"


@pytest.mark.django_db
class TestBoardCreateAPI:
    """Tests for POST /api/boards/ - Create a new board."""

    def test_create_valid_board(self, api_client):
        """Should create board with valid name."""
        payload = {"name": "New Project Board"}

        response = api_client.post('/api/boards/', payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == "New Project Board"
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_reject_empty_name(self, api_client):
        """Should reject empty name with proper error format."""
        payload = {"name": ""}

        response = api_client.post('/api/boards/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'error' in data
        assert 'message' in data
        assert 'field' in data
        assert data['field'] == 'name'

    def test_reject_whitespace_only_name(self, api_client):
        """Should reject whitespace-only name."""
        payload = {"name": "   "}

        response = api_client.post('/api/boards/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['field'] == 'name'

    def test_reject_missing_name(self, api_client):
        """Should reject request without name field."""
        payload = {}

        response = api_client.post('/api/boards/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['field'] == 'name'


@pytest.mark.django_db
class TestBoardRetrieveAPI:
    """Tests for GET /api/boards/{id}/ - Retrieve a specific board."""

    def test_retrieve_existing_board(self, api_client, create_board):
        """Should return board details with tasks."""
        board = create_board(name="My Board")

        response = api_client.get(f'/api/boards/{board.id}/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['id'] == board.id
        assert data['name'] == "My Board"
        assert 'tasks' in data
        assert isinstance(data['tasks'], list)

    def test_retrieve_board_with_tasks(self, api_client, create_board, create_task):
        """Should return board with nested tasks."""
        board = create_board(name="Board With Tasks")
        task1 = create_task(board=board, title="Task 1")
        task2 = create_task(board=board, title="Task 2", status=TaskStatus.IN_PROGRESS)

        response = api_client.get(f'/api/boards/{board.id}/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data['tasks']) == 2
        task_titles = [t['title'] for t in data['tasks']]
        assert "Task 1" in task_titles
        assert "Task 2" in task_titles

    def test_retrieve_nonexistent_board(self, api_client):
        """Should return 404 for non-existent board."""
        response = api_client.get('/api/boards/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert 'error' in data
        assert 'message' in data
        assert 'field' in data
        assert data['field'] is None


@pytest.mark.django_db
class TestBoardDeleteAPI:
    """Tests for DELETE /api/boards/{id}/ - Delete a board."""

    def test_delete_existing_board(self, api_client, create_board):
        """Should delete board and return 204."""
        board = create_board(name="Board To Delete")

        response = api_client.delete(f'/api/boards/{board.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Board.objects.filter(id=board.id).exists()

    def test_delete_board_with_tasks(self, api_client, create_board, create_task):
        """Should delete board and cascade delete its tasks."""
        board = create_board(name="Board With Tasks")
        task = create_task(board=board, title="Task To Cascade Delete")

        response = api_client.delete(f'/api/boards/{board.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Board.objects.filter(id=board.id).exists()
        assert not Task.objects.filter(id=task.id).exists()

    def test_delete_nonexistent_board(self, api_client):
        """Should return 404 for non-existent board."""
        response = api_client.delete('/api/boards/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data['field'] is None


@pytest.mark.django_db
class TestTaskListAPI:
    """Tests for GET /api/boards/{id}/tasks/ - List tasks in a board."""

    def test_list_empty_tasks(self, api_client, create_board):
        """Should return empty list when board has no tasks."""
        board = create_board(name="Empty Board")

        response = api_client.get(f'/api/boards/{board.id}/tasks/')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_tasks(self, api_client, create_board, create_task):
        """Should return list of tasks ordered by created_at."""
        board = create_board(name="Board With Tasks")
        task1 = create_task(board=board, title="First Task")
        task2 = create_task(board=board, title="Second Task")

        response = api_client.get(f'/api/boards/{board.id}/tasks/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]['title'] == "First Task"
        assert data[1]['title'] == "Second Task"

    def test_list_tasks_filter_by_status(self, api_client, create_board, create_task):
        """Should filter tasks by status parameter."""
        board = create_board(name="Board With Mixed Tasks")
        todo_task = create_task(board=board, title="Todo Task", status=TaskStatus.TODO)
        in_progress_task = create_task(board=board, title="In Progress Task", status=TaskStatus.IN_PROGRESS)
        done_task = create_task(board=board, title="Done Task", status=TaskStatus.DONE)

        # Filter by TODO status
        response = api_client.get(f'/api/boards/{board.id}/tasks/', {'status': 'TODO'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == "Todo Task"
        assert data[0]['status'] == "TODO"

    def test_list_tasks_nonexistent_board(self, api_client):
        """Should return 404 when board does not exist."""
        response = api_client.get('/api/boards/99999/tasks/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskCreateAPI:
    """Tests for POST /api/boards/{id}/tasks/ - Create a task."""

    def test_create_valid_task(self, api_client, create_board):
        """Should create task with valid data."""
        board = create_board(name="Board For Tasks")
        payload = {
            "title": "New Task",
            "description": "Task description",
            "status": "TODO"
        }

        response = api_client.post(f'/api/boards/{board.id}/tasks/', payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['title'] == "New Task"
        assert data['description'] == "Task description"
        assert data['status'] == "TODO"
        assert data['board'] == board.id
        assert 'id' in data

    def test_create_task_default_status(self, api_client, create_board):
        """Should create task with default TODO status."""
        board = create_board(name="Board For Tasks")
        payload = {
            "title": "Task Without Status"
        }

        response = api_client.post(f'/api/boards/{board.id}/tasks/', payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['status'] == "TODO"

    def test_create_task_reject_empty_title(self, api_client, create_board):
        """Should reject task with empty title."""
        board = create_board(name="Board For Tasks")
        payload = {
            "title": ""
        }

        response = api_client.post(f'/api/boards/{board.id}/tasks/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['field'] == 'title'

    def test_create_task_reject_whitespace_title(self, api_client, create_board):
        """Should reject task with whitespace-only title."""
        board = create_board(name="Board For Tasks")
        payload = {
            "title": "   "
        }

        response = api_client.post(f'/api/boards/{board.id}/tasks/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['field'] == 'title'

    def test_create_task_reject_invalid_status(self, api_client, create_board):
        """Should reject task with invalid status."""
        board = create_board(name="Board For Tasks")
        payload = {
            "title": "Task With Bad Status",
            "status": "INVALID_STATUS"
        }

        response = api_client.post(f'/api/boards/{board.id}/tasks/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['field'] == 'status'

    def test_create_task_nonexistent_board(self, api_client):
        """Should return 404 when creating task on non-existent board."""
        payload = {
            "title": "Orphan Task"
        }

        response = api_client.post('/api/boards/99999/tasks/', payload, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskUpdateAPI:
    """Tests for PATCH /api/tasks/{id}/ - Update a task."""

    def test_update_task_status(self, api_client, create_task):
        """Should update task status."""
        task = create_task(title="Task To Update", status=TaskStatus.TODO)

        payload = {"status": "IN_PROGRESS"}
        response = api_client.patch(f'/api/tasks/{task.id}/', payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == "IN_PROGRESS"
        assert data['title'] == "Task To Update"  # Unchanged

    def test_update_task_to_done(self, api_client, create_task):
        """Should update task status to DONE."""
        task = create_task(title="Complete Me", status=TaskStatus.IN_PROGRESS)

        payload = {"status": "DONE"}
        response = api_client.patch(f'/api/tasks/{task.id}/', payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['status'] == "DONE"

    def test_update_task_invalid_status(self, api_client, create_task):
        """Should reject invalid status update."""
        task = create_task(title="Task With Invalid Status")

        payload = {"status": "NOT_A_STATUS"}
        response = api_client.patch(f'/api/tasks/{task.id}/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['field'] == 'status'

    def test_update_nonexistent_task(self, api_client):
        """Should return 404 for non-existent task."""
        payload = {"status": "DONE"}
        response = api_client.patch('/api/tasks/99999/', payload, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['field'] is None


@pytest.mark.django_db
class TestTaskDeleteAPI:
    """Tests for DELETE /api/tasks/{id}/ - Delete a task."""

    def test_delete_existing_task(self, api_client, create_task):
        """Should delete task and return 204."""
        task = create_task(title="Task To Delete")

        response = api_client.delete(f'/api/tasks/{task.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()

    def test_delete_nonexistent_task(self, api_client):
        """Should return 404 for non-existent task."""
        response = api_client.delete('/api/tasks/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['field'] is None


@pytest.mark.django_db
class TestErrorResponseFormat:
    """Tests for consistent error response format across all endpoints."""

    def test_400_error_format_validation(self, api_client):
        """All 400 errors should have error, message, and field."""
        payload = {"name": ""}
        response = api_client.post('/api/boards/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'error' in data
        assert 'message' in data
        assert 'field' in data
        assert isinstance(data['field'], str)

    def test_404_error_format_board(self, api_client):
        """All 404 errors should have error, message, and null field."""
        response = api_client.get('/api/boards/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert 'error' in data
        assert 'message' in data
        assert 'field' in data
        assert data['field'] is None

    def test_validation_error_includes_field_name(self, api_client, create_board):
        """Validation errors should specify which field failed."""
        board = create_board()
        payload = {"title": ""}  # Empty title

        response = api_client.post(f'/api/boards/{board.id}/tasks/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['field'] == 'title'


@pytest.mark.django_db
class TestEdgeCases:
    """Tests for edge cases and security concerns."""

    def test_create_task_on_nonexistent_board(self, api_client):
        """Creating task on non-existent board returns 404."""
        payload = {"title": "Orphan Task"}

        response = api_client.post('/api/boards/99999/tasks/', payload, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['field'] is None

    def test_filter_tasks_by_invalid_status(self, api_client, create_board, create_task):
        """Filtering tasks by invalid status returns 400."""
        board = create_board()
        create_task(board=board)

        response = api_client.get(f'/api/boards/{board.id}/tasks/', {'status': 'INVALID'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'status' in str(response.json().get('message', '')).lower() or \
               response.json().get('field') == 'status'

    def test_sql_injection_attempt_in_board_name(self, api_client):
        """SQL injection attempts should be handled safely."""
        payload = {"name": "'; DROP TABLE boards; --"}

        response = api_client.post('/api/boards/', payload, format='json')

        # Should either create the board (safe parameterization) or reject it
        # but should NOT cause any database errors
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        # Verify the table still exists by querying
        assert Board.objects.count() >= 0  # This would fail if table was dropped

    def test_sql_injection_attempt_in_task_title(self, api_client, create_board):
        """SQL injection in task title should be handled safely."""
        board = create_board()
        payload = {
            "title": "'; DELETE FROM tasks; --",
            "description": "Normal description"
        }

        response = api_client.post(f'/api/boards/{board.id}/tasks/', payload, format='json')

        # Should create the task safely or reject it, but not cause SQL errors
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        # Verify tasks table still functions
        assert Task.objects.count() >= 0

    def test_very_long_name_validation(self, api_client):
        """Very long names should be handled properly."""
        # CharField max_length is 255
        long_name = "A" * 300
        payload = {"name": long_name}

        response = api_client.post('/api/boards/', payload, format='json')

        # Should either truncate or reject, but not crash
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_special_characters_in_names(self, api_client):
        """Special Unicode characters should be handled."""
        special_names = [
            "Board with emoji 🚀",
            "中文看板",
            "اللوحة العربية",
            "<script>alert('xss')</script>"
        ]

        for name in special_names:
            payload = {"name": name}
            response = api_client.post('/api/boards/', payload, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()['name'] == name


@pytest.mark.django_db
class TestTaskFilterAPI:
    """Tests for task filtering functionality."""

    def test_filter_by_todo_status(self, api_client, create_board, create_task):
        """Should return only TODO tasks."""
        board = create_board()
        todo_task = create_task(board=board, title="Todo Task", status=TaskStatus.TODO)
        create_task(board=board, title="In Progress Task", status=TaskStatus.IN_PROGRESS)
        create_task(board=board, title="Done Task", status=TaskStatus.DONE)

        response = api_client.get(f'/api/boards/{board.id}/tasks/', {'status': 'TODO'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['id'] == todo_task.id

    def test_filter_by_in_progress_status(self, api_client, create_board, create_task):
        """Should return only IN_PROGRESS tasks."""
        board = create_board()
        create_task(board=board, title="Todo Task", status=TaskStatus.TODO)
        in_progress_task = create_task(board=board, title="In Progress Task", status=TaskStatus.IN_PROGRESS)
        create_task(board=board, title="Done Task", status=TaskStatus.DONE)

        response = api_client.get(f'/api/boards/{board.id}/tasks/', {'status': 'IN_PROGRESS'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['id'] == in_progress_task.id

    def test_filter_by_done_status(self, api_client, create_board, create_task):
        """Should return only DONE tasks."""
        board = create_board()
        create_task(board=board, title="Todo Task", status=TaskStatus.TODO)
        create_task(board=board, title="In Progress Task", status=TaskStatus.IN_PROGRESS)
        done_task = create_task(board=board, title="Done Task", status=TaskStatus.DONE)

        response = api_client.get(f'/api/boards/{board.id}/tasks/', {'status': 'DONE'})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['id'] == done_task.id


@pytest.mark.django_db
class TestBoardOrderingAPI:
    """Tests for board ordering behavior."""

    def test_boards_ordered_by_created_at_desc(self, api_client, create_board):
        """Boards should be returned in descending order of created_at."""
        import time

        board1 = create_board(name="First")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        board2 = create_board(name="Second")
        time.sleep(0.01)
        board3 = create_board(name="Third")

        response = api_client.get('/api/boards/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        # Most recently created should be first
        assert data[0]['id'] == board3.id
        assert data[1]['id'] == board2.id
        assert data[2]['id'] == board1.id


@pytest.mark.django_db
class TestTaskOrderingAPI:
    """Tests for task ordering behavior."""

    def test_tasks_ordered_by_created_at_asc(self, api_client, create_board, create_task):
        """Tasks should be returned in ascending order of created_at."""
        import time

        board = create_board()
        task1 = create_task(board=board, title="First Task")
        time.sleep(0.01)
        task2 = create_task(board=board, title="Second Task")
        time.sleep(0.01)
        task3 = create_task(board=board, title="Third Task")

        response = api_client.get(f'/api/boards/{board.id}/tasks/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        # Should be ordered by created_at ascending
        assert data[0]['id'] == task1.id
        assert data[1]['id'] == task2.id
        assert data[2]['id'] == task3.id
