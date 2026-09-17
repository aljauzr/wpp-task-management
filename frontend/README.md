# Frontend Service - Task Management UI

Independent React frontend for the Mini Task Management application, built with **Next.js**, **React 19**, and **TypeScript**.

---

## 1. Overview

This frontend runs as a separate service and communicates with the backend only through HTTP.

Current UI coverage:
- List all boards and select the active board
- Create a new board
- Show tasks for the selected board
- Create a task with browser-side validation
- Update task status inline
- Delete a task
- Filter tasks by status
- Show loading, empty, request-failure, and backend-down states

The backend base URL is configured through environment variables to satisfy R26.

---

## 2. Directory Structure

```text
frontend/
├── src/
│   ├── components/
│   │   ├── task-manager/      # Board/task UI components and styles
│   │   ├── Header.tsx
│   │   └── Layout.tsx
│   ├── hooks/
│   │   └── useTaskManager.ts  # Frontend state + API orchestration
│   ├── pages/
│   │   ├── _app.tsx
│   │   └── index.tsx
│   ├── services/
│   │   └── api.ts             # Centralized HTTP client
│   └── styles/
│       └── globals.css
├── .env.example
├── package.json
└── README.md
```

---

## 3. Prerequisites

- Node.js `18.x`, `20.x`, or `22.x`
- npm `9+`

---

## 4. Setup and Run

From `frontend/`:

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

Set the backend URL in `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Optional production build:

```bash
npm run build
npm run start
```

---

## 5. API Integration

The frontend uses these backend endpoints:

- `GET /api/boards/`
- `POST /api/boards/`
- `DELETE /api/boards/{id}/`
- `GET /api/boards/{id}/tasks/?status=`
- `POST /api/boards/{id}/tasks/`
- `PATCH /api/tasks/{id}/`
- `DELETE /api/tasks/{id}/`
- `GET /health`

All API calls are centralized in `src/services/api.ts`. Network and API failures are normalized into a shared `ApiError` shape so the UI can handle validation, not-found, and backend-unreachable cases consistently.

---

## 6. UX and State Handling

The main page is driven by `useTaskManager.ts`, which coordinates:

- initial board loading
- task loading for the selected board
- filter changes without page reload
- optimistic-feeling local updates after status changes and deletions
- board/task form validation
- retry flow when the backend is unavailable

The page intentionally stays simple and readable rather than heavily styled.

---

## 7. Verification

Run these checks from `frontend/`:

```bash
npm run build
```

Recommended manual verification:

1. Start the backend on `http://localhost:8000`
2. Start the frontend on `http://localhost:3000`
3. Create a board
4. Create multiple tasks with different statuses
5. Filter tasks by status
6. Update task status from the list
7. Delete a task
8. Stop the backend and refresh the page

Expected backend-down behavior:
- the page still renders
- an error banner is shown
- the user can retry after the backend is started again

---

## 8. Assumptions and Trade-offs

- Board deletion is exposed in the UI even though it is not required by R19-R25, because the API already supports it and it helps verify cascade behavior end to end.
- Frontend tests are still skipped. The brief marks them as optional, and time is better spent on backend tests and submission documentation.
- The UI keeps state local to the page instead of adding a global store because the app is small and has a single main screen.
