# Working in this repo

This repo is a FastAPI + Clerk JWT authentication demo — a runnable learning boilerplate for the login -> JWT -> backend verification flow. Keep changes small and typed.

## Run

```bash
uv sync
cp .env.example .env  # set CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY, CLERK_FRONTEND_API
uv run python main.py
uv run uvicorn app.main:app --reload  # alternative
```

App serves at http://127.0.0.1:8000, API docs at /docs, health at /health.

## Checks

Run the same checks CI runs:

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run mypy app --ignore-missing-imports
uv run pytest -q
```

CI is `.github/workflows/ci.yml` (push/PR to `master`): uv sync, ruff check, ruff format, mypy, pytest.

## Repo expectations

- Branch from `master` as `feat/<short-name>` or `chore/<short-name>`; open a PR — do not push directly to `master`.
- Keep PRs small and include: what changed, how tested, and a screenshot if UI changed.
- Do not commit secrets. `.env` is gitignored; only `.env.example` is committed with placeholder values.
- License is MIT (`LICENSE`).

## Notes for agents

- Follow `docs/` and existing `app/auth/`, `app/core/`, `app/routes/`, `app/schemas/` structure.
- Keep this repo self-contained. Do not add network calls in tests; mock external services.
- Prefer extending existing modules over adding parallel solutions.
