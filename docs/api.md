# API

Base URL: `http://127.0.0.1:8741`

Interactive docs: `/docs` (Swagger) and `/redoc`.

## Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Start OAuth PKCE (`{ "provider": "github" \| "gitlab" }`) |
| GET | `/auth/callback` | Browser redirect landing |
| POST | `/auth/callback` | Exchange code for tokens |
| POST | `/auth/demo-login` | Local demo session |
| POST | `/auth/logout` | Clear local session |
| GET | `/auth/me` | Current user |

## Repositories

| Method | Path | Description |
|--------|------|-------------|
| GET | `/repositories` | List / search (`?q=`) |
| POST | `/repositories` | Connect / clone |
| POST | `/repositories/import` | Import local git path |
| GET | `/repositories/{id}` | Detail |
| DELETE | `/repositories/{id}` | Remove |

## Pull requests

| Method | Path | Description |
|--------|------|-------------|
| GET | `/pullrequests` | List open (optional `repository_id`) |
| GET | `/pullrequests/{id}` | Detail + file diffs |

## Reviews

| Method | Path | Description |
|--------|------|-------------|
| POST | `/reviews/start` | Run multi-agent review |
| GET | `/reviews/{id}` | Review + comments |
| GET | `/reviews/{id}/comments` | Comments only |

## AI providers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/providers` | Catalog + availability |
| PATCH | `/providers` | Set active provider / API keys |

## Settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/settings` | Current settings |
| PATCH | `/settings` | Update settings |

## Dashboard

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard` | Stats, activity, recent reviews |

## Health

| Method | Path |
|--------|------|
| GET | `/health` |
