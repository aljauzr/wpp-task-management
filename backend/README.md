# Backend Service - Task Management API

Independent REST API service for the Mini Task Management Application, built with **Python 3.12+**, **Django 5.1**, and **Django REST Framework (DRF)**.

---

## 1. Stack Choice & Rationale (Section 5)

> **Why Python with Django REST Framework:**
> We chose Python with Django REST Framework because of its mature ORM, robust migration engine, declarative validation serializer pipeline, and clean architectural extensibility. Django provides first-class relational integrity enforcement at the database level (foreign keys, cascading policies, and check constraints) while DRF facilitates a clean separation between HTTP representation and underlying business domain services.

---

## 2. Architecture & Layered Structure (R17)

The backend strictly separates responsibilities into four distinct layers so that business domain logic remains testable in isolation without spinning up an HTTP server:

```
backend/
├── src/
│   ├── config/           # Django settings, WSGI/ASGI, routing
│   ├── controllers/      # HTTP layer: APIView controllers (handles request/response mapping)
│   ├── services/         # Domain layer: Pure business logic (no HTTP concepts)
│   ├── repositories/     # Data access layer: Query abstraction over models
│   ├── models/           # ORM entities: Declarative database schema and constraints
│   └── database/
│       └── migrations/   # Managed database migration files
├── tests/                # Unit tests and API integration tests
├── requirements.txt      # Python dependencies
├── manage.py             # Django entry point
├── .env.example          # Environment variables template
└── README.md             # This documentation
```

1. **Controllers (`src/controllers/`)**: Parse HTTP parameters, invoke domain services, and serialize JSON responses with explicit HTTP status codes.
2. **Services (`src/services/`)**: Implement business rules, validation, and domain flows without dependencies on Django HTTP requests or responses.
3. **Repositories (`src/repositories/`)**: Encapsulate ORM queries and data persistence operations.
4. **Models (`src/models/`)**: Define database tables, data types, constraints, and relationships.

---

## 3. Prerequisites

- **Python**: `3.12+` (with `pip` and `venv`)
- **Database**:
  - **PostgreSQL 14+** (Recommended for production/Docker environments)
  - **SQLite3** (Built-in; automatically used if `DATABASE_URL` is omitted, ensuring a clean clone runs out-of-the-box without setup friction)

---

## 4. Setup & Run Instructions (Clean Clone)

### Step 1: Create and Activate Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell):
.venv\Scripts\Activate.ps1

# Activate (Linux / macOS / Git Bash):
# source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
cp .env.example .env
```

Review `.env`:
- To connect to a PostgreSQL database:
  ```env
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/task_management
  ```
- If `DATABASE_URL` is left empty, the application automatically uses a local `db.sqlite3` file.

### Step 4: Run Database Migrations (R6)

```bash
python manage.py migrate
```

This applies all framework migrations as well as application migrations (`src/database/migrations/0001_initial.py`), generating the `boards` and `tasks` tables with all constraints and indexes.

### Step 5: Start the Development Server

```bash
python manage.py runserver 8000
```

The service will start on:
- Base URL: `http://localhost:8000`
- Health Endpoint: `http://localhost:8000/health`

---

## 5. Database Schema & Design (R1 - R7)

The full relational schema, column definitions, constraints, and trade-off rationales are documented in [SCHEMA.md](SCHEMA.md).

### Summary of Tables:
- **`boards`** (R1): `id` (PK, BigInt), `name` (VARCHAR(255), non-empty check constraint), `created_at`, `updated_at`.
- **`tasks`** (R2, R3, R4): `id` (PK, BigInt), `board_id` (FK referencing `boards.id` with `ON DELETE CASCADE`), `title` (VARCHAR(255), non-empty check constraint), `description` (TEXT), `status` (VARCHAR(20), choices: `TODO`, `IN_PROGRESS`, `DONE`, default: `TODO`, check constraint), `created_at`, `updated_at`.

### Enforced Constraints & Indexes:
- **Foreign Key Constraint (R3)**: Enforced at the database engine level (`db_constraint=True`).
- **Cascade Deletion (R4)**: Deleting a board cascades to delete its tasks (`ON DELETE CASCADE`), ensuring no orphaned tasks.
- **Composite Indexes (R5)**:
  - `idx_tasks_board_status` (`board_id`, `status`) to optimize `GET /api/boards/{id}/tasks?status=...`.
  - `idx_tasks_board_created` (`board_id`, `created_at`) to optimize chronological task queries within a board.

### Architectural Decisions Considered & Rejected (R7):
1. **Status lookup table**: Rejected in favor of `VARCHAR(20)` with a DB `CHECK` constraint to avoid unnecessary join overhead for a fixed 3-state workflow.
2. **Soft deletes (`is_deleted`)**: Rejected because the application is a lightweight spreadsheet replacement without audit requirements; hard cascade delete avoids query complexity and orphan handling.
3. **UUID vs BigInt PKs**: Rejected UUIDs in favor of `BigAutoField` to keep REST routes clean (`/api/boards/1/tasks`) and optimize B-Tree index performance.

---

## 6. Running the Tests (R27, R28, R30)

Tests run using Django's built-in test runner or `pytest`.

### Execute Test Suite:

```bash
python manage.py test
```

Or with `pytest`:

```bash
pytest
```

The test suite currently validates 11 tests across:
- **Database Models & Constraints (`tests/test_models.py`)**:
  - Creation of boards and tasks with defaults.
  - Rejection of empty board names (`CHECK (name != '')`).
  - Rejection of empty task titles (`CHECK (title != '')`).
  - Rejection of invalid task statuses (`CHECK (status IN (...))`).
  - Cascade deletion of tasks when a parent board is deleted (`ON DELETE CASCADE`).
  - Enforcement of foreign key relationships at the database level.
- **Business Domain & Health API (`tests/test_health.py`)**:
  - Domain rules in `HealthService` without web server.
  - HTTP status codes and contract on `GET /health`.

---

## 7. API Contract (Current Endpoints)

### Health Check

- **Method**: `GET`
- **Path**: `/health` (or `/health/`)
- **Description**: Proves backend service liveness and reachability.
- **Request Body**: None
- **Response (200 OK)**:
  ```json
  {
    "status": "ok"
  }
  ```
- **Error Response (500 Internal Server Error)**:
  ```json
  {
    "error": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred"
  }
  ```

---

## 8. Assumptions & Trade-offs (Section 8)

- **Database Engine Dual-Mode**: PostgreSQL is configured as the primary production engine. However, we configured automatic fallback to SQLite when `DATABASE_URL` is not specified so reviewers can verify the codebase immediately without launching a PostgreSQL instance.
- **Migration Location**: Django migrations are configured to output into `src/database/migrations/` via `MIGRATION_MODULES` to adhere cleanly to the requested folder layout.

