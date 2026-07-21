# Contributing

Thanks for helping improve Open Review.

## Principles

1. **Local-first** — no feature may require hosted project infrastructure.
2. **Privacy-first** — telemetry stays off by default; secrets stay encrypted locally.
3. **Provider-agnostic** — AI logic belongs behind the `AIProvider` interface.
4. **Replaceable agents** — review specialists implement `ReviewAgent`.

## Workflow

1. Fork and branch from `main`.
2. Make focused changes with tests.
3. Run backend `pytest` and frontend `npm test` / `npm run build`.
4. Open a PR with a clear summary and test plan.

## Code style

- Python: Ruff + Black, Python 3.13, type hints
- TypeScript: strict mode, ESLint/oxlint, Prettier
- Prefer small, composable modules over monoliths

## License

Contributions are accepted under the Apache License 2.0.
