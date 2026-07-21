# Development

## Prerequisites

- Node.js 20+
- Python 3.13+
- Rust toolchain (for Tauri)
- Optional: [Ollama](https://ollama.com) for local models

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn openreview.main:app --reload --port 8741
```

OpenAPI docs: http://127.0.0.1:8741/docs

```bash
pytest
ruff check src tests
```

## Frontend

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm test
npm run build
```

Set `VITE_API_URL` if the API is not on `http://127.0.0.1:8741`.

## Desktop (Tauri)

With the backend venv installed:

```bash
cd frontend
npm run tauri:dev
```

Production installers:

```bash
npm run tauri:build
```

## OAuth (optional)

Register a GitHub / GitLab OAuth app with redirect URI:

```text
http://127.0.0.1:8741/auth/callback
```

Export:

```bash
export OPENREVIEW_GITHUB_CLIENT_ID=...
export OPENREVIEW_GITHUB_CLIENT_SECRET=...
export OPENREVIEW_GITLAB_CLIENT_ID=...
export OPENREVIEW_GITLAB_CLIENT_SECRET=...
```

Without OAuth credentials, use **Demo sign-in** from onboarding / profile.

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENREVIEW_HOST` | `127.0.0.1` | API bind host |
| `OPENREVIEW_PORT` | `8741` | API port |
| `OPENREVIEW_DATA_DIR` | OS app data | SQLite location |
| `OPENREVIEW_REPOS_DIR` | `~/AIReviewer/repos` | Clone root |
| `OPENREVIEW_DEFAULT_AI_PROVIDER` | `ollama` | Default provider |
| `OPENREVIEW_TELEMETRY_ENABLED` | `false` | Always off by default |
