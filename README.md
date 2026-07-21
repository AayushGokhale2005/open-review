# Open Review

**Your code stays on your machine.**

Open Review is an open-source, local-first AI code review desktop application inspired by CodeRabbit — designed to run entirely on your machine with **zero infrastructure required from project maintainers**.

## Philosophy

- **Local-first** — no hosted backend, no cloud database
- **Privacy-first** — your source never leaves your machine unless you choose
- **BYOK** — bring your own AI keys or run fully offline with Ollama
- **Provider-agnostic** — Ollama, LM Studio, vLLM, OpenAI, Anthropic, OpenRouter
- **Apache 2.0** — truly open source

## Architecture

```text
Tauri Desktop Shell
        │
        ▼
React Frontend  ──localhost REST──▶  Embedded FastAPI Backend
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     │ SQLite · Local Git · AI Providers · Reviews │
                     └─────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.13+
- Rust (for Tauri builds)
- [Ollama](https://ollama.com) (recommended for local AI)

### Development

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn openreview.main:app --reload --port 8741

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Desktop (Tauri)

```bash
cd frontend
npm install
npm run tauri dev
```

## Features

- Connect GitHub & GitLab via OAuth PKCE (localhost callback)
- Clone / import local repositories into `~/AIReviewer/repos/`
- AI-powered PR review with modular specialist agents
- Diff viewer, inline comments, approve / request changes
- Dark-mode UI with command palette (⌘K)
- Settings for models, strictness, ignored paths, custom rules

## Tech Stack

| Layer     | Stack                                              |
|-----------|----------------------------------------------------|
| Desktop   | Tauri 2, Rust                                      |
| Frontend  | React 19, TypeScript, Vite, Tailwind, shadcn/ui    |
| Backend   | FastAPI, SQLAlchemy 2, SQLite, Pydantic v2         |
| AI        | Provider abstraction (Ollama default)              |

## Documentation

- [Architecture](docs/architecture.md)
- [Development](docs/development.md)
- [API](docs/api.md)
- [Contributing](docs/contributing.md)

## License

Apache License 2.0 — see [LICENSE](LICENSE).
