# Mini Task Management Application

Study Case Submission for **Executive Full Stack Developer - WPP Media**.

## Current Progress

The project now covers the full required flow:

- backend schema, migrations, service layer, API endpoints, and tests
- frontend board/task management UI with loading, empty, filter, and backend-down states
- submission-facing documentation for setup, schema, API contract, assumptions, and trade-offs

For a concise requirement-by-requirement summary, see [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md).

---

## 1. Project Overview & Architecture

This repository contains a mini task management application architected strictly as **two independent, decoupled services** communicating exclusively over HTTP via REST API:

- **`backend/`**: Built with **Python 3.12+**, **Django 5.1**, and **Django REST Framework (DRF)**. Utilizes PostgreSQL (with automatic SQLite fallback for zero-config clean runs) with migrations configured in `database/migrations/`, structured in distinct architectural layers (`controllers` → `services` → `repositories` → `models`).
- **`frontend/`**: Built with **React 19**, **Next.js**, and **TypeScript**. Configurable backend API base URL, resilient error boundaries, and connection health status handling.

```text
wpp-task-management/
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
│   ├── API.md                # API contract and request/response examples
│   ├── SCHEMA.md             # Detailed database schema & trade-offs (R5, R7)
│   └── README.md             # Backend setup & architecture guide
│
├── frontend/                 # Independent Next.js React UI service
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Next.js pages
│   │   ├── services/         # HTTP API client
│   │   ├── hooks/            # Custom React hooks
│   │   └── styles/           # CSS styles
│   ├── package.json          # Node dependencies & scripts
│   ├── .env.example          # Frontend environment template
│   └── README.md             # Frontend setup & configuration guide
│
├── .gitignore                # Global ignore rules
├── SUBMISSION_CHECKLIST.md   # Requirement summary for final review
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

# 5. Run backend tests (recommended)
python -m pytest -q

# 6. Start the server
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

# 3. Verify production build (recommended)
npm run build

# 4. Start development server
npm run dev
```
- Application UI: `http://localhost:3000`

---

## 4. Verification & Self-Check

Recommended checks before submission:

1. Backend only:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/boards/
   ```
2. Frontend only:
   - stop the backend
   - open `http://localhost:3000`
   - confirm the page still renders and shows the backend-unavailable banner
3. Full flow:
   - create a board
   - create tasks with different statuses
   - filter tasks by status
   - update a task status inline
   - delete a task
   - delete a board and confirm its tasks are removed

---

## 5. Detailed Documentation

For service-specific design decisions, API contracts, schema documentation, and testing guides:
- [Backend Documentation](backend/README.md)
- [Backend API Contract](backend/API.md)
- [Database Schema](backend/SCHEMA.md)
- [Frontend Documentation](frontend/README.md)
- [Submission Checklist](SUBMISSION_CHECKLIST.md)
