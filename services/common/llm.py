"""LLM client backed by OpenAI. Drop-in replacement for the Anthropic version.

Swap OPUS_MODEL / HAIKU_MODEL in .env to change which models are used.
  smart tier → gpt-4o       (complex reasoning)
  fast  tier → gpt-4o-mini  (simple / cheap)
"""
from __future__ import annotations
import os
from typing import Iterable, Literal
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from .config import get_settings

_settings = get_settings()
_client = OpenAI(api_key=_settings.openai_api_key or os.getenv("OPENAI_API_KEY", ""))

Tier = Literal["fast", "smart"]


def _model_for(tier: Tier) -> str:
    return _settings.haiku_model if tier == "fast" else _settings.opus_model


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def complete(
    system: str,
    messages: list[dict],
    tier: Tier = "smart",
    max_tokens: int = 1024,
    temperature: float = 0.2,
    cache_system: bool = True,   # kept for API compatibility; OpenAI caches automatically
) -> str:
    """One-shot completion."""
    full_messages = [{"role": "system", "content": system}] + messages
    resp = _client.chat.completions.create(
        model=_model_for(tier),
        messages=full_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def stream(
    system: str,
    messages: list[dict],
    tier: Tier = "smart",
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> Iterable[str]:
    full_messages = [{"role": "system", "content": system}] + messages
    with _client.chat.completions.stream(
        model=_model_for(tier),
        messages=full_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    ) as s:
        for chunk in s:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
