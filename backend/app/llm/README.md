# llm

The LLM router: the single module every other part of the backend calls through to reach Groq or Gemini (see `PROJECT_PLAN_v2.md` Section 10.1). No other module talks to a provider directly.

**Inputs:** a task description/prompt from `app/services`, current provider rate state from Redis.
**Outputs:** a model completion plus recorded token usage (`ModelUsageLog`), with automatic failover between providers and a template-only fallback if both are unavailable. Implemented in Phase 4 — this session only stubs the module.
