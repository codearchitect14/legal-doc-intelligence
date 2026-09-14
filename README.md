# Legal Doc Intelligence

Production-grade legal documentation automation platform. Full plan: [`PROJECT_PLAN_v2.md`](PROJECT_PLAN_v2.md).

## Setup

1. Copy the environment template and fill in real values:
   ```
   cp .env.example .env
   ```
2. Start Postgres (with pgvector) and Redis:
   ```
   docker compose up -d db redis
   ```
3. Install backend dependencies and run migrations:
   ```
   cd backend
   uv sync
   uv run alembic upgrade head
   ```
4. Run the backend:
   ```
   uv run uvicorn app.main:app --reload
   ```
5. Run tests:
   ```
   uv run pytest
   ```

## Repository layout

See `PROJECT_PLAN_v2.md` Section 8 for the full repository structure rationale. Each backend package and frontend folder has its own `README.md` describing its purpose, inputs, and outputs.

## Git discipline

This repository has a single contributor. Before every commit and push, verify `git config user.name` / `git config user.email` and `git remote -v` match this repository's identity — see `PROJECT_PLAN_v2.md` Section 20.
