# Backend Service - Task Management API

Independent REST API service for the Mini Task Management Application, built with **Python 3.12+**, **Django 5.1**, and **Django REST Framework (DRF)**.

---

## 1. Stack Choice & Rationale (Section 5)

> **Why Python with Django REST Framework:**
> We chose Python with Django REST Framework because of its mature ORM, migration engine, and support for a clear separation between HTTP handling and business services. Foreign keys and check constraints enforce data integrity in the database; an explicit migration also enforces board/task cascade deletion independently of Django's ORM.

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

### Service Layer (Commit 3)

| Service | Operations |
|---|---|
| `BoardService` | `list_boards()`, `get_board(board_id)`, `create_board(name)`, `delete_board(board_id)` |
| `TaskService` | `get_task(task_id)`, `list_tasks(board_id, status=None)`, `create_task(board_id, title, description="", status="TODO")`, `update_status(task_id, status)`, `delete_task(task_id)` |

Services accept injected repositories for isolated unit tests and use Django-backed repositories by default. They return model instances/lists, or `None` for deletion. Models are also used as data objects in unit tests; ORM queries and writes stay in repositories. This keeps the implementation small without adding a second set of domain entities.

Expected failures use plain Python exceptions in `src/services/exceptions.py`:
- `ValidationError`: `code="VALIDATION_FAILED"`, a useful `message`, and the invalid `field`.
- `NotFoundError`: `code="NOT_FOUND"`, a `message`, `resource`, and `entity_id`; `field` is `None`.

Neither exception contains an HTTP status or response object. The controller layer maps them to consistent JSON error responses, while unexpected persistence errors still surface as server errors instead of being disguised as validation failures.

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

This applies all framework and application migrations in `src/database/migrations/`: `0001` creates the tables, constraints, and indexes; `0002` adds database-enforced board/task cascade deletion. Use the same command to upgrade an existing database; no data reset is needed.

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
- **`tasks`** (R2, R3, R4): `id` (PK, BigInt), `board_id` (FK referencing `boards.id` with database cascade), `title` (VARCHAR(255), non-empty check constraint), `description` (TEXT), `status` (VARCHAR(20), choices: `TODO`, `IN_PROGRESS`, `DONE`, ORM default: `TODO`, check constraint), `created_at`, `updated_at`.

### Enforced Constraints & Indexes:
- **Foreign Key Constraint (R3)**: Enforced at the database engine level (`db_constraint=True`).
- **Deletion Policy (R4)**: Deleting a board removes its tasks, including through direct SQL. Migration `0002` installs PostgreSQL's native `ON DELETE CASCADE` FK or SQLite's equivalent `boards_delete_tasks` database trigger. Both execute transactionally; neither depends on application cleanup.
- **Composite Indexes (R5)**:
  - `idx_tasks_board_status` (`board_id`, `status`) to optimize `GET /api/boards/{id}/tasks?status=...`.
  - `idx_tasks_board_created` (`board_id`, `created_at`) to optimize chronological task queries within a board.

### Architectural Decisions Considered & Rejected (R7):
1. **Status lookup table**: Rejected in favor of `VARCHAR(20)` with a DB `CHECK` constraint to avoid unnecessary join overhead for a fixed 3-state workflow.
2. **Soft deletes (`is_deleted`)**: Rejected because the application is a lightweight spreadsheet replacement without audit requirements; hard cascade delete avoids query complexity and orphan handling.
3. **UUID vs BigInt PKs**: Rejected UUIDs in favor of `BigAutoField` to keep REST routes clean (`/api/boards/1/tasks`) and optimize B-Tree index performance.

---

## 6. Running the Tests (R27, R28, R30)

Run these commands from `backend/`, with the virtual environment activated and dependencies installed.

### Execute Test Suite:

```bash
python -m pytest -q
```

This is the canonical command for the **complete** suite. The suite is intentionally focused on business rules, failure paths, and database guarantees that would catch a real regression. `python manage.py test` is not a substitute for the full suite.

Run only isolated service unit tests (no database access):

```bash
python -m pytest tests/test_board_service.py tests/test_task_service.py -q
```

Run only service/repository integration tests:

```bash
python -m pytest tests/test_service_integration.py -q
```

Run only database cascade and migration regression tests:

```bash
python -m pytest tests/test_database_cascade.py tests/test_cascade_migration.py -q
```

Run only API integration tests:

```bash
python -m pytest tests/test_api_integration.py -q
```

No running backend or frontend server is needed. Pytest-django blocks database access in the service unit tests; their repositories are autospecced mocks. Integration tests use a separate, temporary test database, not the application's data. With `DATABASE_URL` empty they use SQLite; when it targets PostgreSQL, the database server must be running and the user needs permission to create a test database.

The backend suite was last verified locally on SQLite with `70 passed`. PostgreSQL was also verified for the database-cascade regression coverage introduced in commit 4.

Current breakdown:
- `tests/test_task_service.py`: 21 focused unit tests for task validation, filtering, missing-resource handling, and invalid-status failures.
- `tests/test_api_integration.py`: 20 focused API tests covering the documented board/task endpoints and their required 400/404 paths.
- `tests/test_board_service.py`: 10 focused unit tests for board validation and missing-board handling.
- `tests/test_service_integration.py`: 8 service/repository integration tests for persistence, scoped filtering, invalid status updates, and cascade behavior through real repositories.
- `tests/test_models.py`: 5 schema-level tests for DB constraints and foreign-key enforcement.
- `tests/test_database_cascade.py`: 3 direct-SQL regression tests for database-enforced cascade and rollback behavior.
- `tests/test_health.py`: 2 tests for the health service and `GET /health`.
- `tests/test_cascade_migration.py`: 1 migration regression test for upgrade, reversal, and reapplication.

The suite focuses on the behaviors called out by the brief:
- service-layer validation and failure cases
- required 400/404 API behavior
- board/task filtering and status updates
- real foreign-key enforcement and database-level delete behavior
- migration safety for the schema decision made in R4

---

## 7. API Contract (Current Endpoints)

The backend currently exposes:

- `GET /health`
- `GET /api/boards/`
- `POST /api/boards/`
- `GET /api/boards/{id}/`
- `DELETE /api/boards/{id}/`
- `GET /api/boards/{id}/tasks/?status=`
- `POST /api/boards/{id}/tasks/`
- `PATCH /api/tasks/{id}/`
- `DELETE /api/tasks/{id}/`

All failures use a single JSON envelope:

```json
{
  "error": "VALIDATION_FAILED",
  "message": "Title cannot be empty or whitespace-only.",
  "field": "title"
}
```

The full request/response contract, examples, and cURL snippets are documented in [API.md](API.md).

---

## 8. Assumptions & Trade-offs (Section 8)

- **Database Engine Dual-Mode**: PostgreSQL is configured as the primary production engine. However, we configured automatic fallback to SQLite when `DATABASE_URL` is not specified so reviewers can verify the codebase immediately without launching a PostgreSQL instance.
- **Migration Location**: Django migrations are configured to output into `src/database/migrations/` via `MIGRATION_MODULES` to adhere cleanly to the requested folder layout.
- **Required Text**: Board names and task titles are trimmed before checking that they contain 1-255 characters. Missing, `None`, and non-string values are rejected. Duplicate board names and task titles are allowed.
- **Description**: Omission means an empty string. Explicit `None` or non-string values are rejected; valid text is preserved, including whitespace and line breaks.
- **Status**: Creation defaults to `TODO` when omitted. Explicit values and filters must exactly match `TODO`, `IN_PROGRESS`, or `DONE`; an empty filter is invalid. Any transition between valid statuses, including reapplying the current status, is allowed.
- **Lookup Precedence**: Resource existence is checked before validating task fields/filters. IDs are expected to be integers, with URL parsing delegated to the future HTTP layer.
- **Ordering**: Boards are listed newest first and tasks oldest first, following model ordering. Order within identical creation timestamps is unspecified.
- **Scope**: Updates currently change only status. Editing a task title/description, pagination, authentication, and bulk import are intentionally out of scope.
- **Database Cascade Maintenance**: Django's `on_delete` does not generate SQL cascade rules. Migration `0002` supplies them explicitly; future table rebuilds/FK replacements must preserve the custom rule or trigger. See [SCHEMA.md](SCHEMA.md) for the implementation and rollback trade-offs.
- **Database Choice**: PostgreSQL is the preferred target for reviewer parity with the brief. SQLite remains the default local fallback so the project starts from a clean clone with no separate database setup.
- **Known Limitation**: The database rejects empty strings, but whitespace-only protection is implemented in the service/controller layer rather than as a database `CHECK` using trimmed values.
- **Frontend Testing**: Frontend automated tests are intentionally skipped because the brief marks them as optional. Time was prioritized toward backend business-rule and API coverage.
