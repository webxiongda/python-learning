# Python FastAPI Learning Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Python learning workbench with FastAPI backend, React frontend, and AI-ready interview practice boundaries.

**Architecture:** The backend reads existing Markdown course content and stores user state in SQLite through SQLAlchemy. The frontend mirrors the Java workbench and talks to matching `/api` routes. AI-dependent scoring is isolated behind the interview service and uses deterministic local feedback in the first version.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Pydantic, pytest, React, Vite, TypeScript, lucide-react, react-markdown.

---

### Task 1: Backend Foundation

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/auth.py`
- Create: `backend/app/course_content.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/test_workbench_api.py`

- [ ] Write failing tests for course parsing, auth, progress validation, self-check cards, and interview attempts.
- [ ] Run `python3 -m pytest backend/tests/test_workbench_api.py -q` and confirm the tests fail before implementation.
- [ ] Implement FastAPI app, SQLAlchemy models, auth helpers, and content parsing.
- [ ] Run backend tests and fix failures.

### Task 2: Learning And Interview APIs

**Files:**
- Create: `backend/app/learning_service.py`
- Create: `backend/app/interview_service.py`
- Create: `backend/app/api/auth.py`
- Create: `backend/app/api/learning.py`
- Create: `backend/app/api/interview.py`
- Modify: `backend/app/main.py`

- [ ] Implement user routes under `/api/auth`.
- [ ] Implement learning routes under `/api`.
- [ ] Implement interview routes under `/api/interview`.
- [ ] Run `python3 -m pytest backend/tests/test_workbench_api.py -q`.

### Task 3: React Workbench

**Files:**
- Create: `package.json`
- Create: `index.html`
- Create: `tsconfig.json`
- Create: `tsconfig.node.json`
- Create: `tsconfig.app.json`
- Create: `vite.config.ts`
- Create: `src/main.tsx`
- Create: `src/App.tsx`
- Create: `src/styles.css`

- [ ] Build the React shell with login, dashboard, today, study, cards, portfolio, and interview views.
- [ ] Render Markdown layers from the FastAPI chapter endpoint.
- [ ] Wire validation, self-check, review card, portfolio, and interview actions to the backend.
- [ ] Run `npm install`, `npm run check`, and `npm run build`.

### Task 4: Repository Commands And Verification

**Files:**
- Modify: `Makefile`
- Create: `backend/README.md`

- [ ] Add backend and frontend verification commands without removing existing learning content checks.
- [ ] Document local startup commands.
- [ ] Run `python3 -m pytest backend/tests/test_workbench_api.py -q`.
- [ ] Run `make all`.
- [ ] Run `npm run build`.
