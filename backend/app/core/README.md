# core

Configuration, security primitives, and shared request dependencies.

**Inputs:** environment variables (via `config.py`'s `Settings`), incoming request tokens.
**Outputs:** a single typed settings object, password hashing/JWT helpers, and FastAPI dependencies (`get_current_user`, `require_role`, firm-scoping) used by every route.
