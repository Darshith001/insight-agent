"""/chat endpoint: SSE streaming of the agent answer with citations + critique."""
from __future__ import annotations
import asyncio
import json
import time
import traceback
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import httpx
from sse_starlette.sse import EventSourceResponse

from services.common.config import get_settings
from services.common.tracing import trace
from services.agent.graph import run as run_agent
from ..auth import current_user
from ..ratelimit import check as rl_check
from ..cache import lookup as cache_lookup, store as cache_store
from ..guardrails import is_injection, redact_pii
from ..metrics import QUERIES, LATENCY, CRITIQUE

router = APIRouter()


class ChatReq(BaseModel):
    question: str
    force_tier: str | None = None  # "fast" | "smart" | None


async def _route_tier(q: str) -> str:
    s = get_settings()
    try:
        async with httpx.AsyncClient(timeout=2.0) as cli:
            r = await cli.post(f"{s.router_url}/route", json={"question": q})
            r.raise_for_status()
            return r.json()["tier"]
    except Exception:
        return "smart" if len(q.split()) > 24 else "fast"


@router.post("/chat")
async def chat(req: ChatReq, user: str = Depends(current_user)):
    rl_check(user)
    q = req.question.strip()
    if not q:
        raise HTTPException(400, "empty question")
    if is_injection(q):
        raise HTTPException(400, "input rejected by guardrails")
    q = redact_pii(q)

    tier = req.force_tier or await _route_tier(q)
    t0 = time.perf_counter()

    # run cache lookup in thread (it loads embeddings — don't block event loop)
    cached = await asyncio.to_thread(cache_lookup, q)
    if cached:
        QUERIES.labels(tier=tier, cache="hit").inc()

        async def gen_cached():
            yield {"event": "tier", "data": json.dumps({"tier": tier, "cache": True})}
            yield {"event": "answer", "data": json.dumps({"text": cached["answer"]})}
            yield {"event": "citations", "data": json.dumps(cached["citations"])}
            yield {"event": "done", "data": json.dumps({"latency": time.perf_counter() - t0})}

        return EventSourceResponse(gen_cached())

    async def gen():
        try:
            with trace("chat", user=user, tier=tier, question=q):
                yield {"event": "tier", "data": json.dumps({"tier": tier, "cache": False})}

                result = await asyncio.to_thread(run_agent, q, tier)

                QUERIES.labels(tier=tier, cache="miss").inc()
                CRITIQUE.observe(float(result["critique"].get("score", 1.0)))
                LATENCY.labels(tier=tier).observe(time.perf_counter() - t0)

                await asyncio.to_thread(cache_store, q,
                    {"answer": result["answer"], "citations": result["citations"]})

                yield {"event": "answer", "data": json.dumps({"text": result["answer"]})}
                yield {"event": "citations", "data": json.dumps(result["citations"])}
                yield {"event": "critique", "data": json.dumps(result["critique"])}
                yield {"event": "done", "data": json.dumps({
                    "latency": time.perf_counter() - t0,
                    "retries": result["retries"],
                    "sub_queries": result["sub_queries"],
                })}
        except Exception as e:
            # surface the error to the client instead of silently closing the stream
            err = traceback.format_exc()
            print(f"[chat error] {err}")
            yield {"event": "error", "data": json.dumps({"message": str(e), "detail": err})}

    return EventSourceResponse(gen())
