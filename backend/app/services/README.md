# services

Business logic: extraction, classification, chronology assembly, damages/totals calculation, and draft generation (implemented in later phases per `PROJECT_PLAN_v2.md` Sections 6 and 14).

**Inputs:** validated schemas from `app/api`, ORM sessions.
**Outputs:** persisted/updated model state, returned to `app/api` for serialization.
