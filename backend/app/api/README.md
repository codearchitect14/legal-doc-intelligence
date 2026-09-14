# api

REST route definitions grouped by resource (auth, firms, users, cases, documents).

**Inputs:** HTTP requests, validated against Pydantic schemas in `app/schemas`.
**Outputs:** JSON responses; delegates business logic to `app/services`.
