"""Semantic cache backed by Redis. Gracefully disabled if Redis is not running."""
from __future__ import annotations
import json
import hashlib
import numpy as np
import redis
from services.common.config import get_settings
from services.common.embeddings import embed

_THRESHOLD = 0.92
_EMB_KEY = "scache:emb"
_VAL_KEY = "scache:val"


def _get_redis():
    try:
        r = redis.Redis.from_url(get_settings().redis_url, decode_responses=True, socket_connect_timeout=1)
        r.ping()
        return r
    except Exception:
        return None


def _key_for(q: str) -> str:
    return hashlib.sha1(q.lower().strip().encode()).hexdigest()[:20]


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def lookup(question: str) -> dict | None:
    r = _get_redis()
    if r is None:
        return None   # cache disabled — skip silently
    try:
        v = np.asarray(embed([question])["dense"][0], dtype=np.float32)
        keys = r.hkeys(_EMB_KEY)[:500]
        best_key, best_sim = None, 0.0
        for k in keys:
            raw = r.hget(_EMB_KEY, k)
            if not raw:
                continue
            cand = np.frombuffer(bytes.fromhex(raw), dtype=np.float32)
            sim = _cos(v, cand)
            if sim > best_sim:
                best_sim, best_key = sim, k
        if best_key and best_sim >= _THRESHOLD:
            val = r.hget(_VAL_KEY, best_key)
            if val:
                return {"hit": True, "similarity": best_sim, **json.loads(val)}
    except Exception:
        pass
    return None


def store(question: str, answer: dict, ttl_s: int = 86400) -> None:
    r = _get_redis()
    if r is None:
        return   # cache disabled — skip silently
    try:
        v = np.asarray(embed([question])["dense"][0], dtype=np.float32)
        k = _key_for(question)
        r.hset(_EMB_KEY, k, v.tobytes().hex())
        r.hset(_VAL_KEY, k, json.dumps(answer))
        r.expire(_EMB_KEY, ttl_s)
        r.expire(_VAL_KEY, ttl_s)
    except Exception:
        pass
