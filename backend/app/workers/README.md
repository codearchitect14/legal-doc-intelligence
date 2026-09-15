# workers

Background job definitions (OCR, classification, extraction) that run asynchronously so large uploads never block the web application.

**Inputs:** job payloads enqueued by `app/api` (e.g. a newly uploaded document ID).
**Outputs:** updated document/case state in the database. Implemented starting Phase 2 - this session only stubs the module.
