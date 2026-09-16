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

### Step 5: Start the Development Server

```bash
python manage.py runserver 8000
```

The service will start on:
- Base URL: `http://localhost:8000`
- Health Endpoint: `http://localhost:8000/health`

---

## 5. Running the Tests (R27, R28, R30)

Tests run using Django's built-in test runner or `pytest`.

### Execute Test Suite:

```bash
python manage.py test
```

Or with `pytest`:

```bash
pytest
```

The test suite validates:
- Business domain rules in `HealthService` without starting a web server (`HealthServiceUnitTest`).
- HTTP API contract and status codes on `GET /health` (`HealthControllerIntegrationTest`).

---

## 6. API Contract (Initial Endpoints)

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

## 7. Assumptions & Trade-offs (Section 8)

- **Database Engine Dual-Mode**: PostgreSQL is configured as the primary production engine. However, we configured automatic fallback to SQLite when `DATABASE_URL` is not specified so reviewers can verify the codebase immediately without launching a PostgreSQL instance.
- **Migration Location**: Django migrations are configured to output into `src/database/migrations/` via `MIGRATION_MODULES` to adhere cleanly to the requested folder layout.
