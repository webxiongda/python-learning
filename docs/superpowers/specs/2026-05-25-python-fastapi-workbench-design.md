# Python FastAPI Learning Workbench Design

## Goal

Build a Python learning workbench that mirrors the Java study project while using FastAPI as the primary backend framework and keeping future AI application features easy to add.

## Current Context

The repository already contains a 60 chapter Python learning roadmap, chapter Markdown files, project workspaces, and a quality check script. It does not yet have the application layer that exists in `java-study`: authenticated learning dashboard, progress tracking, validation records, review scheduling, portfolio evidence, and interview practice.

## Recommended Approach

Use a React + Vite frontend with a FastAPI backend. Keep the API shape close to `java-study` so the frontend can reuse the same product model, but implement the backend in idiomatic Python:

- FastAPI for HTTP routing and dependency injection.
- SQLAlchemy 2.x for persistence.
- SQLite for local default storage.
- Pydantic models for request and response contracts.
- Markdown content loaded directly from `README.md` and `chapters/`.
- A separate AI service boundary for later model scoring, streaming responses, RAG, and agent tools.

## Architecture

The backend is organized by responsibility:

- `app/main.py` creates the FastAPI app, database tables, routers, and startup seed data.
- `app/database.py` owns SQLAlchemy engine/session creation.
- `app/models.py` defines persisted entities.
- `app/schemas.py` defines API contracts.
- `app/auth.py` handles password hashing, signed tokens, and current user resolution.
- `app/course_content.py` parses the existing Markdown roadmap and chapter files.
- `app/learning_service.py` handles progress, validation, review tasks, review cards, notes, mistakes, logs, and portfolio evidence.
- `app/interview_service.py` handles Python/FastAPI/AI interview categories, questions, attempts, and stats.

The frontend is a Vite React app modeled after the Java workbench. It calls the FastAPI routes under `/api`, stores the auth token in `localStorage`, renders Markdown chapter content, and exposes the same core views: dashboard, today, study, cards, portfolio, and interview.

## Data Flow

1. A user registers or logs in.
2. The frontend stores the returned token and sends it as `Authorization: Bearer <token>`.
3. The backend reads chapter metadata from `README.md` and chapter content from the existing Markdown files.
4. User-specific state is stored in SQLite: progress, validations, review tasks, review cards, notes, mistakes, portfolio evidence, and interview attempts.
5. Completing all four chapter layers creates +3, +7, and +30 review tasks.
6. Failed self-checks create a mistake and a next-day review card.
7. Project validations automatically create portfolio evidence.

## AI Extension Boundary

The first version does not call an external model. It prepares for AI work by:

- Keeping interview answer submission behind a service method.
- Returning deterministic local feedback for now.
- Naming categories and data around Python, FastAPI, and AI application backend work.
- Leaving model-dependent behavior isolated so later OpenAI Responses API streaming, structured scoring, RAG retrieval, and agent tool execution can be added without rewriting learning progress logic.

## Error Handling

API errors use FastAPI exceptions with clear Chinese messages for user-facing validation failures. Authentication failures return `401`. Missing resources return `404`. Validation errors for summaries, evidence, and answers return `400`.

## Testing

Backend tests cover:

- Course metadata and chapter content parsing from the repository.
- Authentication and current-user guarded routes.
- Validation completion and review task creation.
- Failed self-check creation of mistakes and review cards.
- Interview question listing and attempt recording.

Frontend verification covers TypeScript build and Vite production build.

## Scope Exclusions

This version does not include external AI API calls, vector databases, RAG ingestion, multi-user deployment hardening, migrations, or production OAuth. Those belong in later increments after the local workbench is stable.
