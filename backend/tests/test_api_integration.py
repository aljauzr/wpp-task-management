"""Focused API integration tests for the documented board and task flows."""

import time

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Board, Task, TaskStatus


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_board():
    def _create_board(name="Test Board"):
        return Board.objects.create(name=name)

    return _create_board


@pytest.fixture
def create_task(create_board):
    def _create_task(board=None, title="Test Task", description="", status=TaskStatus.TODO):
        if board is None:
            board = create_board()
        return Task.objects.create(
            board=board,
            title=title,
            description=description,
            status=status,
        )

    return _create_task


@pytest.mark.django_db
def test_list_boards_returns_newest_first(api_client, create_board):
    first = create_board(name="First Board")
    time.sleep(0.01)
    second = create_board(name="Second Board")

    response = api_client.get("/api/boards/")

    assert response.status_code == status.HTTP_200_OK
    assert [board["id"] for board in response.json()] == [second.id, first.id]


@pytest.mark.django_db
def test_create_board_returns_created_resource(api_client):
    response = api_client.post("/api/boards/", {"name": "New Project Board"}, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Project Board"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.django_db
@pytest.mark.parametrize("name", ["", "   "])
def test_create_board_rejects_blank_name(api_client, name):
    response = api_client.post("/api/boards/", {"name": name}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"] == "VALIDATION_FAILED"
    assert data["field"] == "name"


@pytest.mark.django_db
def test_retrieve_board_returns_nested_tasks(api_client, create_board, create_task):
    board = create_board(name="Board With Tasks")
    create_task(board=board, title="Task 1")
    create_task(board=board, title="Task 2", status=TaskStatus.IN_PROGRESS)

    response = api_client.get(f"/api/boards/{board.id}/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == board.id
    assert [task["title"] for task in data["tasks"]] == ["Task 1", "Task 2"]


@pytest.mark.django_db
def test_retrieve_nonexistent_board_returns_404(api_client):
    response = api_client.get("/api/boards/99999/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"] == "NOT_FOUND"
    assert data["field"] is None


@pytest.mark.django_db
def test_delete_board_cascades_to_its_tasks(api_client, create_board, create_task):
    board = create_board(name="Board With Tasks")
    task = create_task(board=board, title="Task To Delete")

    response = api_client.delete(f"/api/boards/{board.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Board.objects.filter(id=board.id).exists()
    assert not Task.objects.filter(id=task.id).exists()


@pytest.mark.django_db
def test_list_tasks_filters_by_status(api_client, create_board, create_task):
    board = create_board(name="Board With Mixed Tasks")
    create_task(board=board, title="Todo Task", status=TaskStatus.TODO)
    done_task = create_task(board=board, title="Done Task", status=TaskStatus.DONE)

    response = api_client.get(f"/api/boards/{board.id}/tasks/", {"status": "DONE"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == done_task.id


@pytest.mark.django_db
def test_list_tasks_rejects_invalid_status_filter(api_client, create_board, create_task):
    board = create_board()
    create_task(board=board)

    response = api_client.get(f"/api/boards/{board.id}/tasks/", {"status": "INVALID"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"] == "VALIDATION_FAILED"
    assert data["field"] == "status"


@pytest.mark.django_db
def test_list_tasks_for_nonexistent_board_returns_404(api_client):
    response = api_client.get("/api/boards/99999/tasks/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["field"] is None


@pytest.mark.django_db
def test_create_task_returns_created_resource(api_client, create_board):
    board = create_board(name="Board For Tasks")

    response = api_client.post(
        f"/api/boards/{board.id}/tasks/",
        {"title": "New Task", "description": "Task description"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Task"
    assert data["description"] == "Task description"
    assert data["status"] == "TODO"
    assert data["board"] == board.id


@pytest.mark.django_db
@pytest.mark.parametrize("title", ["", "   "])
def test_create_task_rejects_blank_title(api_client, create_board, title):
    board = create_board(name="Board For Tasks")

    response = api_client.post(
        f"/api/boards/{board.id}/tasks/",
        {"title": title},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"] == "VALIDATION_FAILED"
    assert data["field"] == "title"


@pytest.mark.django_db
def test_create_task_rejects_invalid_status(api_client, create_board):
    board = create_board(name="Board For Tasks")

    response = api_client.post(
        f"/api/boards/{board.id}/tasks/",
        {"title": "Task With Bad Status", "status": "INVALID_STATUS"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["field"] == "status"


@pytest.mark.django_db
def test_create_task_on_nonexistent_board_returns_404(api_client):
    response = api_client.post(
        "/api/boards/99999/tasks/",
        {"title": "Orphan Task"},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["field"] is None


@pytest.mark.django_db
def test_update_task_status_returns_updated_resource(api_client, create_task):
    task = create_task(title="Task To Update", status=TaskStatus.TODO)

    response = api_client.patch(
        f"/api/tasks/{task.id}/",
        {"status": "IN_PROGRESS"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["title"] == "Task To Update"


@pytest.mark.django_db
def test_update_task_rejects_invalid_status(api_client, create_task):
    task = create_task(title="Task With Invalid Status")

    response = api_client.patch(
        f"/api/tasks/{task.id}/",
        {"status": "NOT_A_STATUS"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["field"] == "status"


@pytest.mark.django_db
def test_update_nonexistent_task_returns_404(api_client):
    response = api_client.patch(
        "/api/tasks/99999/",
        {"status": "DONE"},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["field"] is None


@pytest.mark.django_db
def test_delete_existing_task_returns_204(api_client, create_task):
    task = create_task(title="Task To Delete")

    response = api_client.delete(f"/api/tasks/{task.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Task.objects.filter(id=task.id).exists()


@pytest.mark.django_db
def test_delete_nonexistent_task_returns_404(api_client):
    response = api_client.delete("/api/tasks/99999/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["field"] is None
