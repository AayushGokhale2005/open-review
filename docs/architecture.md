# Architecture

Open Review is a **local-first desktop application**. There is no hosted backend, cloud database, or project-owned infrastructure.

```text
┌─────────────────────────────────────────────────────────────┐
│                     Tauri Desktop Shell                     │
│  (spawns embedded FastAPI on 127.0.0.1:8741, owns window)   │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     React + Vite UI                 FastAPI Backend
     (localhost:5173 / bundled)      SQLite · Git · AI · OAuth
```

## Layers

### Desktop (`frontend/src-tauri`)

- Tauri 2 + Rust
- Starts / stops the Python backend with the app lifecycle
- Bundles the React build for macOS, Windows, and Linux

### Frontend (`frontend`)

- React 19, TypeScript, Tailwind, TanStack Query, Zustand
- Feature pages: landing, onboarding, dashboard, repos, PRs, reviews, providers, settings
- Talks only to `http://127.0.0.1:8741`

### Backend (`backend`)

Clean architecture with dependency injection:

| Package | Responsibility |
|---------|----------------|
| `api/` | REST routes + OpenAPI |
| `core/` | Settings, DI container, security, logging |
| `db/` | SQLAlchemy session, seed data |
| `models/` | SQLite ORM entities |
| `repositories/` | Data access (repository pattern) |
| `schemas/` | Pydantic v2 DTOs |
| `services/ai/` | Provider abstraction (Ollama default) |
| `services/git/` | Clone / pull / diff under `~/AIReviewer/repos/` |
| `services/oauth/` | GitHub/GitLab PKCE + localhost callback |
| `services/review/` | Modular multi-agent review pipeline |

## Review pipeline

```text
Indexer → Diff Extractor → Context Builder → Planner
       → Security → Performance → Architecture → Style → Maintainability
       → Merge Results → Review Output
```

Each agent implements `ReviewAgent` and can be replaced (future: LangGraph, CrewAI, Tree-sitter).

## Data

SQLite lives in the OS application data directory (`platformdirs`).

Tables: users, oauth_accounts, repositories, pull_requests, reviews, review_comments, settings, cached_metadata, audit_logs.

## Extensibility hooks

Designed without major refactor for:

- Tree-sitter AST analysis
- Semantic search / local embeddings / Qdrant / LanceDB
- GitHub/GitLab webhooks
- Enterprise multi-user self-hosted mode
- Remote review workers
