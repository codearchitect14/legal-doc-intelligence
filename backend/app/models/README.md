# models

SQLAlchemy ORM models mirroring the data model in `PROJECT_PLAN_v2.md` Section 12.

**Inputs:** none (declarative schema definitions).
**Outputs:** table definitions used by Alembic migrations and by `app/services` for queries. Every tenant-scoped table carries a `firm_id` column enforced at the query layer.
