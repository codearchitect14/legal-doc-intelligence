# Setup

1. Copy `.env.example` to `.env` at the repository root and fill in real values (never commit `.env`).
2. `docker compose up -d db redis`
3. `cd backend && uv sync`
4. `uv run alembic upgrade head`
5. `uv run uvicorn app.main:app --reload`
6. `uv run pytest`

See the root `README.md` for more detail.
