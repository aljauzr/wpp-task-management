# Frontend Service - Task Management UI

Independent web client application for the Mini Task Management Application, built with **React 19**, **Next.js**, and **TypeScript**.

---

## 1. Overview & Separation of Concerns

This frontend service is completely decoupled from the backend. It:
- Communicates **strictly over HTTP** via REST API calls.
- Encapsulates network operations in `src/services/api.ts`.
- Configures the backend base URL via environment variables (R26 compliant - not hardcoded).
- Implements resilient error boundaries and status indicators (passes Section 4 Self-Check 2: if the backend is stopped, the application still loads gracefully without crashing or throwing blank screens).

---

## 2. Directory Structure

```
frontend/
├── src/
│   ├── components/       # UI Components (Header, HealthCard, Layout)
│   ├── pages/            # Next.js Pages (_app.tsx, _document.tsx, index.tsx)
│   ├── services/         # Centralized HTTP API client (reads config URL)
│   ├── hooks/            # Custom React hooks (useHealthCheck)
│   └── styles/           # CSS design system (globals.css)
├── package.json          # Dependencies and npm scripts
├── tsconfig.json         # TypeScript configuration
├── next.config.js        # Next.js configuration
├── .env.example          # Environment variables template
├── .env.local            # Local environment file (git-ignored)
└── README.md             # This documentation
```

---

## 3. Prerequisites

- **Node.js**: `18.x`, `20.x`, or `22.x`
- **npm**: `9.x+` (or `yarn` / `pnpm`)

---

## 4. Setup & Run Instructions (Clean Clone)

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Configure Environment Variables (R26)

```bash
cp .env.example .env.local
```

Ensure `NEXT_PUBLIC_API_BASE_URL` points to your backend instance:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

> **Note on Compatibility:** We also support `VITE_API_BASE_URL` in `src/services/api.ts` if running under different tooling standards.

### Step 3: Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Step 4: Production Build (Optional)

```bash
npm run build
npm run start
```

---

## 5. Self-Check Verification (Section 4 Compliance)

### Self-Check 2: Backend Stopped Test
1. Make sure the backend Django server is **not running**.
2. Start the frontend: `npm run dev`.
3. Open `http://localhost:3000`.
4. **Result**: The page loads cleanly, showing `Backend: Disconnected` with a helpful description and a button to re-check connection. No blank screen, uncaught error, or crash occurs.
5. Start the backend in another terminal (`python manage.py runserver 8000`).
6. Click "Check Connection" in the UI: the indicator turns to `Backend: Connected` with `status: "ok"`.
