# Open Review

Local-first AI code review for developers who keep their source on their machine.

## Quick commands

```bash
# API
cd backend && source .venv/bin/activate && uvicorn openreview.main:app --reload --port 8741

# UI
cd frontend && npm run dev

# Desktop
cd frontend && npm run tauri:dev
```

See [docs/development.md](docs/development.md) for full setup.
