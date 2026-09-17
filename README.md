# Mini Task Management Application

Study Case Submission for **Executive Full Stack Developer - WPP Media**.

## Current Progress

Commit 3 adds `BoardService` and `TaskService`, repository-backed persistence, domain validation/errors, and isolated unit tests plus database integration tests. Run the complete backend suite from `backend/` with `python -m pytest -q`.

Only `/health` is currently exposed over HTTP. Board/task REST endpoints and uniform error handling are next (commit 4), followed by the task-management UI (commit 5) and final documentation/self-checks (commit 6).

**R4 follow-up completed:** Migration `0002` enforces cascade deletion through PostgreSQL's `ON DELETE CASCADE` FK or an equivalent SQLite database trigger. Direct-SQL and migration regression tests verify deletion, rollback, and preservation of existing data. Run `python manage.py migrate` to update existing databases. See [schema details](backend/SCHEMA.md).

---

## 1. Project Overview & Architecture

This repository contains a mini task management application architected strictly as **two independent, decoupled services** communicating exclusively over HTTP via REST API:

- **`backend/`**: Built with **Python 3.12+**, **Django 5.1**, and **Django REST Framework (DRF)**. Utilizes PostgreSQL (with automatic SQLite fallback for zero-config clean runs) with migrations configured in `database/migrations/`, structured in distinct architectural layers (`controllers` → `services` → `repositories` → `models`).
- **`frontend/`**: Built with **React 19**, **Next.js**, and **TypeScript**. Configurable backend API base URL, resilient error boundaries, and connection health status handling.

```
wpp-task-managemment/
├── backend/                  # Independent Django REST API service
│   ├── src/
│   │   ├── config/           # Django settings, URLs, WSGI/ASGI
│   │   ├── controllers/      # HTTP request handling (API views)
│   │   ├── services/         # Business domain logic
│   │   ├── repositories/     # Data access layer
│   │   ├── models/           # Django ORM models
│   │   └── database/         # Schema migrations
│   ├── tests/                # Unit & integration tests
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Backend environment template
│   ├── SCHEMA.md             # Detailed database schema & trade-offs (R5, R7)
│   └── README.md             # Backend setup & architecture guide
│
├── frontend/                 # Independent Next.js React UI service
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Next.js pages
│   │   ├── services/         # HTTP API client
│   │   ├── hooks/            # Custom React hooks (health check, etc.)
│   │   └── styles/           # CSS styles
│   ├── package.json          # Node dependencies & scripts
│   ├── .env.example          # Frontend environment template
│   └── README.md             # Frontend setup & configuration guide
│
├── .gitignore                # Global ignore rules
└── README.md                 # Root documentation (this file)
```

---

## 2. Prerequisites

- **Python**: `3.12+` (with `pip` and `venv`)
- **Node.js**: `18.x` or `20.x` or `22.x` (with `npm 9+`)
- **Database**: PostgreSQL `14+` (application defaults to SQLite if `DATABASE_URL` is omitted, allowing immediate review out of the box)

---

## 3. Quick Start (Running Both Services)

Both services are decoupled and started independently in separate terminals.

### Terminal 1: Start Backend (Port 8000)

```bash
cd backend

# 1. Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env

# 4. Apply database migrations
python manage.py migrate

# 5. Start the server
python manage.py runserver 8000
```
- API Base URL: `http://localhost:8000`
- Health Check: `http://localhost:8000/health` (returns `{"status": "ok"}`)

### Terminal 2: Start Frontend (Port 3000)

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Environment configuration
cp .env.example .env.local

# 3. Start development server
npm run dev
```
- Application UI: `http://localhost:3000`

---

## 4. Verification & Self-Check (Section 4 Compliance)

As specified in the assessment guidelines, the two services must pass the two-minute separation test:

1. **Test 1 — Backend Standalone**:
   - Stop the frontend.
   - Leave the backend running.
   - Run in terminal:
     ```bash
     curl -i http://localhost:8000/health
     ```
   - **Expected Result**: HTTP `200 OK` with body `{"status":"ok"}`.

2. **Test 2 — Frontend Resiliency (Backend Down)**:
   - Stop the backend process.
   - Access `http://localhost:3000` in the browser.
   - **Expected Result**: Frontend loads cleanly, showing a clear, friendly status (`Backend: Disconnected`) with connection instructions and a retry button. No crash, no blank screen, and no uncaught exceptions.

---

## 5. Detailed Documentation

For service-specific design decisions, API contracts, schema documentation, and testing guides:
- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
