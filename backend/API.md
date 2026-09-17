# API Documentation

Complete REST API documentation for the Task Management backend service.

## Base URL

```
http://localhost:8000
```

## Content-Type

All requests and responses use JSON:

```
Content-Type: application/json
```

---

## Endpoints Overview

| Method | Endpoint | Description | Requirement |
|--------|----------|-------------|-------------|
| GET | `/health` | Health check endpoint | - |
| GET | `/api/boards/` | List all boards | R8 |
| POST | `/api/boards/` | Create a new board | R9 |
| GET | `/api/boards/{id}/` | Get board details | - |
| DELETE | `/api/boards/{id}/` | Delete a board | R14 |
| GET | `/api/boards/{id}/tasks/?status=` | List tasks for a board | R10 |
| POST | `/api/boards/{id}/tasks/` | Create a task on a board | R11 |
| PATCH | `/api/tasks/{id}/` | Update task status | R12 |
| DELETE | `/api/tasks/{id}/` | Delete a task | R13 |

---

## Health Check

### GET /health

Checks whether the backend service is available.

**Request:**
```http
GET /health
```

**Response 200 OK:**
```json
{
  "status": "ok"
}
```

---

## Board Endpoints

### GET /api/boards/

Returns all available boards. Boards are ordered by `created_at` in descending order, with the newest board first.

**Request:**
```http
GET /api/boards/
```

**Response 200 OK:**
```json
[
  {
    "id": 2,
    "name": "Project Beta",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "tasks": []
  },
  {
    "id": 1,
    "name": "Project Alpha",
    "created_at": "2024-01-10T08:00:00Z",
    "updated_at": "2024-01-12T14:20:00Z",
    "tasks": [
      {
        "id": 1,
        "board": 1,
        "title": "Setup repository",
        "description": "Initialize git repo",
        "status": "DONE",
        "created_at": "2024-01-10T09:00:00Z",
        "updated_at": "2024-01-11T10:00:00Z"
      }
    ]
  }
]
```

---

### POST /api/boards/

Creates a new board.

**Request:**
```http
POST /api/boards/
Content-Type: application/json

{
  "name": "New Project Board"
}
```

**Validation:**
- `name`: required, must not be empty or whitespace-only, maximum 255 characters

**Response 201 Created:**
```json
{
  "id": 3,
  "name": "New Project Board",
  "created_at": "2024-01-20T08:30:00Z",
  "updated_at": "2024-01-20T08:30:00Z",
  "tasks": []
}
```

**Error Response 400 Bad Request:**
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Name cannot be empty or whitespace-only.",
  "field": "name"
}
```

---

### GET /api/boards/{id}/

Returns the details of a board by ID.

**Request:**
```http
GET /api/boards/1/
```

**Response 200 OK:**
```json
{
  "id": 1,
  "name": "Project Alpha",
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-12T14:20:00Z",
  "tasks": [
    {
      "id": 1,
      "board": 1,
      "title": "Setup repository",
      "description": "Initialize git repo",
      "status": "DONE",
      "created_at": "2024-01-10T09:00:00Z",
      "updated_at": "2024-01-11T10:00:00Z"
    }
  ]
}
```

**Error Response 404 Not Found:**
```json
{
  "error": "NOT_FOUND",
  "message": "Board with id 999 does not exist.",
  "field": null
}
```

---

### DELETE /api/boards/{id}/

Deletes a board and all related tasks through cascade deletion.

**Request:**
```http
DELETE /api/boards/1/
```

**Response 204 No Content:**

(empty body)

**Error Response 404 Not Found:**
```json
{
  "error": "NOT_FOUND",
  "message": "Board with id 999 does not exist.",
  "field": null
}
```

---

## Task Endpoints

### GET /api/boards/{id}/tasks/?status=

Returns all tasks for a given board. The result can be filtered by status.

**Request:**
```http
GET /api/boards/1/tasks/
GET /api/boards/1/tasks/?status=TODO
GET /api/boards/1/tasks/?status=IN_PROGRESS
GET /api/boards/1/tasks/?status=DONE
```

**Query Parameters:**
- `status` (optional): filter by status. Valid values are `TODO`, `IN_PROGRESS`, and `DONE`

**Response 200 OK:**
```json
[
  {
    "id": 1,
    "board": 1,
    "title": "Setup repository",
    "description": "Initialize git repo",
    "status": "TODO",
    "created_at": "2024-01-10T09:00:00Z",
    "updated_at": "2024-01-11T10:00:00Z"
  },
  {
    "id": 2,
    "board": 1,
    "title": "Write tests",
    "description": "Create unit tests",
    "status": "IN_PROGRESS",
    "created_at": "2024-01-11T10:00:00Z",
    "updated_at": "2024-01-12T11:00:00Z"
  }
]
```

**Error Response 400 Bad Request (Invalid Status):**
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Invalid status. Must be one of: TODO, IN_PROGRESS, DONE",
  "field": "status"
}
```

**Error Response 404 Not Found:**
```json
{
  "error": "NOT_FOUND",
  "message": "Board with id 999 does not exist.",
  "field": null
}
```

---

### POST /api/boards/{id}/tasks/

Creates a new task on a specific board.

**Request:**
```http
POST /api/boards/1/tasks/
Content-Type: application/json

{
  "title": "Implement feature",
  "description": "Add new functionality",
  "status": "TODO"
}
```

**Validation:**
- `title`: required, must not be empty or whitespace-only, maximum 255 characters
- `description`: optional, default is an empty string
- `status`: optional, default is `TODO`. Valid values are `TODO`, `IN_PROGRESS`, and `DONE`

**Response 201 Created:**
```json
{
  "id": 3,
  "board": 1,
  "title": "Implement feature",
  "description": "Add new functionality",
  "status": "TODO",
  "created_at": "2024-01-20T09:00:00Z",
  "updated_at": "2024-01-20T09:00:00Z"
}
```

**Error Response 400 Bad Request (Empty Title):**
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Title cannot be empty or whitespace-only.",
  "field": "title"
}
```

**Error Response 400 Bad Request (Invalid Status):**
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Invalid status. Must be one of: TODO, IN_PROGRESS, DONE",
  "field": "status"
}
```

**Error Response 404 Not Found:**
```json
{
  "error": "NOT_FOUND",
  "message": "Board with id 999 does not exist.",
  "field": null
}
```

---

### PATCH /api/tasks/{id}/

Updates the status of an existing task.

**Request:**
```http
PATCH /api/tasks/1/
Content-Type: application/json

{
  "status": "DONE"
}
```

**Validation:**
- `status`: required, valid values are `TODO`, `IN_PROGRESS`, and `DONE`

**Response 200 OK:**
```json
{
  "id": 1,
  "board": 1,
  "title": "Setup repository",
  "description": "Initialize git repo",
  "status": "DONE",
  "created_at": "2024-01-10T09:00:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}
```

**Error Response 400 Bad Request (Invalid Status):**
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Invalid status. Must be one of: TODO, IN_PROGRESS, DONE",
  "field": "status"
}
```

**Error Response 404 Not Found:**
```json
{
  "error": "NOT_FOUND",
  "message": "Task with id 999 does not exist.",
  "field": null
}
```

---

### DELETE /api/tasks/{id}/

Deletes a task by ID.

**Request:**
```http
DELETE /api/tasks/1/
```

**Response 204 No Content:**

(empty body)

**Error Response 404 Not Found:**
```json
{
  "error": "NOT_FOUND",
  "message": "Task with id 999 does not exist.",
  "field": null
}
```

---

## Error Response Format

All error responses use a consistent JSON structure:

### 400 Bad Request (Validation Error)

```json
{
  "error": "VALIDATION_FAILED",
  "message": "Description of what went wrong",
  "field": "field_name"
}
```

### 404 Not Found

```json
{
  "error": "NOT_FOUND",
  "message": "Resource with id X does not exist.",
  "field": null
}
```

### 500 Internal Server Error

```json
{
  "error": "INTERNAL_ERROR",
  "message": "An unexpected error occurred.",
  "field": null
}
```

---

## HTTP Status Codes Summary

| Status Code | Meaning |
|-------------|---------|
| 200 OK | The request succeeded and returned data |
| 201 Created | The resource was created successfully |
| 204 No Content | The request succeeded and returned no body |
| 400 Bad Request | Validation error or invalid request |
| 404 Not Found | The requested resource was not found |
| 500 Internal Server Error | An unexpected server error occurred |

---

## Data Types

### Board Object

```json
{
  "id": 1,                          // integer, read-only
  "name": "Board Name",             // string, required, max 255 chars
  "created_at": "2024-01-01T00:00:00Z",  // datetime, read-only (ISO 8601)
  "updated_at": "2024-01-01T00:00:00Z",  // datetime, read-only (ISO 8601)
  "tasks": []                       // array of Task objects, read-only
}
```

### Task Object

```json
{
  "id": 1,                          // integer, read-only
  "board": 1,                       // integer, board ID (read-only on update)
  "title": "Task Title",            // string, required, max 255 chars
  "description": "Description",     // string, optional, default ""
  "status": "TODO",                 // string, optional, default "TODO"
                                    // enum: "TODO", "IN_PROGRESS", "DONE"
  "created_at": "2024-01-01T00:00:00Z",  // datetime, read-only (ISO 8601)
  "updated_at": "2024-01-01T00:00:00Z"   // datetime, read-only (ISO 8601)
}
```

---

## Request/Response Examples

### 1. Create a New Board

**Request:**
```http
POST /api/boards/
Content-Type: application/json

{
  "name": "Development Roadmap"
}
```

**Response 201 Created:**
```json
{
  "id": 1,
  "name": "Development Roadmap",
  "created_at": "2024-01-20T08:00:00Z",
  "updated_at": "2024-01-20T08:00:00Z",
  "tasks": []
}
```

---

### 2. Get the Board List

**Request:**
```http
GET /api/boards/
```

**Response 200 OK:**
```json
[
  {
    "id": 2,
    "name": "Marketing Campaign",
    "created_at": "2024-01-18T10:00:00Z",
    "updated_at": "2024-01-18T10:00:00Z",
    "tasks": []
  },
  {
    "id": 1,
    "name": "Development Roadmap",
    "created_at": "2024-01-15T08:00:00Z",
    "updated_at": "2024-01-15T08:00:00Z",
    "tasks": [
      {
        "id": 1,
        "board": 1,
        "title": "Setup CI/CD",
        "description": "Configure GitHub Actions",
        "status": "IN_PROGRESS",
        "created_at": "2024-01-15T09:00:00Z",
        "updated_at": "2024-01-16T10:00:00Z"
      }
    ]
  }
]
```

---

### 3. Create a Task on a Board

**Request:**
```http
POST /api/boards/1/tasks/
Content-Type: application/json

{
  "title": "Implement authentication",
  "description": "Add JWT-based authentication",
  "status": "TODO"
}
```

**Response 201 Created:**
```json
{
  "id": 2,
  "board": 1,
  "title": "Implement authentication",
  "description": "Add JWT-based authentication",
  "status": "TODO",
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}
```

---

### 4. Get Tasks Filtered by Status

**Request:**
```http
GET /api/boards/1/tasks/?status=IN_PROGRESS
```

**Response 200 OK:**
```json
[
  {
    "id": 1,
    "board": 1,
    "title": "Setup CI/CD",
    "description": "Configure GitHub Actions",
    "status": "IN_PROGRESS",
    "created_at": "2024-01-15T09:00:00Z",
    "updated_at": "2024-01-16T10:00:00Z"
  }
]
```

---

### 5. Update Task Status

**Request:**
```http
PATCH /api/tasks/2/
Content-Type: application/json

{
  "status": "DONE"
}
```

**Response 200 OK:**
```json
{
  "id": 2,
  "board": 1,
  "title": "Implement authentication",
  "description": "Add JWT-based authentication",
  "status": "DONE",
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T14:00:00Z"
}
```

---

### 6. Delete a Task

**Request:**
```http
DELETE /api/tasks/2/
```

**Response 204 No Content:**

(empty body)

---

### 7. Delete a Board with Cascade

**Request:**
```http
DELETE /api/boards/1/
```

**Response 204 No Content:**

(empty body)

**Note:** Deleting a board automatically deletes all related tasks through cascade deletion.

---

## Error Scenarios

### Validation Error Examples

**Empty Board Name:**
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Name cannot be empty or whitespace-only.",
  "field": "name"
}
```

**Empty Task Title:**
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Title cannot be empty or whitespace-only.",
  "field": "title"
}
```

**Title Too Long:**
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Title cannot exceed 255 characters.",
  "field": "title"
}
```

**Invalid Status:**
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Invalid status. Must be one of: TODO, IN_PROGRESS, DONE",
  "field": "status"
}
```

### Not Found Examples

**Board Not Found:**
```json
{
  "error": "NOT_FOUND",
  "message": "Board with id 999 does not exist.",
  "field": null
}
```

**Task Not Found:**
```json
{
  "error": "NOT_FOUND",
  "message": "Task with id 999 does not exist.",
  "field": null
}
```

---

## Requirements Mapping

| Requirement | Endpoint | Method |
|-------------|----------|--------|
| R8 - List boards | `/api/boards/` | GET |
| R9 - Create board | `/api/boards/` | POST |
| R10 - List tasks by board | `/api/boards/{id}/tasks/` | GET |
| R11 - Create task | `/api/boards/{id}/tasks/` | POST |
| R12 - Update task status | `/api/tasks/{id}/` | PATCH |
| R13 - Delete task | `/api/tasks/{id}/` | DELETE |
| R14 - Delete board | `/api/boards/{id}/` | DELETE |

---

## Testing with cURL

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Board
```bash
curl -X POST http://localhost:8000/api/boards/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Board"}'
```

### List Boards
```bash
curl http://localhost:8000/api/boards/
```

### Create Task
```bash
curl -X POST http://localhost:8000/api/boards/1/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Task",
    "description": "Task description",
    "status": "TODO"
  }'
```

### List Tasks with Filter
```bash
curl "http://localhost:8000/api/boards/1/tasks/?status=TODO"
```

### Update Task Status
```bash
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "DONE"}'
```

### Delete Task
```bash
curl -X DELETE http://localhost:8000/api/tasks/1/
```

### Delete Board (with cascade)
```bash
curl -X DELETE http://localhost:8000/api/boards/1/
```

---

## Changelog

### Commit 4 - REST API Implementation
- Implemented the Board ViewSet for endpoints R8, R9, and R14
- Implemented the Task ViewSet for endpoints R10, R11, R12, and R13
- Added a consistent JSON error response format
- Added HTTP status code mapping
- Added this API documentation
