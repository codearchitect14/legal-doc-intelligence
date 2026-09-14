# schemas

Pydantic request and response schemas, separate from the SQLAlchemy models in `app/models`.

**Inputs:** raw request bodies/query params from `app/api`.
**Outputs:** validated Python objects for `app/services`, and serialized response payloads.
