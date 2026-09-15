import logging
import time
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.redis_client import get_redis
from app.models.model_usage_log import ModelUsageLog

logger = logging.getLogger(__name__)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

_UNAVAILABLE_KEY = "llm:{provider}:unavailable"


class ProviderError(Exception):
    """Raised when a single provider call fails after its retries are exhausted."""


def is_provider_available(provider: str) -> bool:
    return get_redis().get(_UNAVAILABLE_KEY.format(provider=provider)) is None


def mark_unavailable(provider: str) -> None:
    settings = get_settings()
    get_redis().set(
        _UNAVAILABLE_KEY.format(provider=provider),
        "1",
        ex=settings.llm_provider_cooldown_seconds,
    )


def _call_with_retries(fn, *args) -> tuple[str, int, int]:
    settings = get_settings()
    last_error: Exception | None = None
    for attempt in range(settings.llm_max_retries + 1):
        try:
            return fn(*args)
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            last_error = exc
            if attempt < settings.llm_max_retries:
                time.sleep(0.1 * (2**attempt))
    raise ProviderError(str(last_error)) from last_error


def _call_groq(prompt: str) -> tuple[str, int, int]:
    settings = get_settings()
    response = httpx.post(
        GROQ_CHAT_URL,
        headers={"Authorization": f"Bearer {settings.groq_api_key}"},
        json={
            "model": settings.groq_model,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return text, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)


def _call_gemini(prompt: str) -> tuple[str, int, int]:
    settings = get_settings()
    url = GEMINI_URL_TEMPLATE.format(model=settings.gemini_model)
    response = httpx.post(
        url,
        params={"key": settings.gemini_api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    usage = data.get("usageMetadata", {})
    return text, usage.get("promptTokenCount", 0), usage.get("candidatesTokenCount", 0)


def _case_token_usage(case_id: UUID, db: Session) -> int:
    rows = db.execute(
        select(ModelUsageLog.input_tokens, ModelUsageLog.output_tokens).where(
            ModelUsageLog.case_id == case_id
        )
    ).all()
    return sum(input_tokens + output_tokens for input_tokens, output_tokens in rows)


def generate_narrative(prompt: str, case_id: UUID, db: Session) -> str | None:
    """The LLM router's failover orchestration (Section 10.1): try Groq, then
    Gemini, recording usage on success. Never raises — returns None if the
    token budget is exhausted or both providers are unavailable, so a case
    is never left without output; the caller falls back to a template."""
    settings = get_settings()
    if _case_token_usage(case_id, db) >= settings.max_tokens_per_case:
        logger.warning(
            "case exceeded its token budget; skipping LLM call",
            extra={"case_id": str(case_id), "max_tokens_per_case": settings.max_tokens_per_case},
        )
        return None

    for provider, call_fn in (("groq", _call_groq), ("gemini", _call_gemini)):
        if not is_provider_available(provider):
            continue
        try:
            text, input_tokens, output_tokens = _call_with_retries(call_fn, prompt)
        except ProviderError:
            logger.exception(
                "LLM provider call failed",
                extra={"provider": provider, "case_id": str(case_id)},
            )
            mark_unavailable(provider)
            continue

        logger.info(
            "LLM call succeeded",
            extra={
                "provider": provider,
                "case_id": str(case_id),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )
        db.add(
            ModelUsageLog(
                case_id=case_id,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        )
        db.commit()
        return text

    return None
