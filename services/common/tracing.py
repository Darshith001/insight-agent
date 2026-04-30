"""Langfuse tracing helpers - no-op if env vars are unset or Langfuse API changes."""
from __future__ import annotations
from contextlib import contextmanager
from functools import lru_cache
from .config import get_settings


@lru_cache
def get_langfuse():
    s = get_settings()
    if not (s.langfuse_public_key and s.langfuse_secret_key):
        return None
    if s.langfuse_public_key.startswith("pk-lf-..."):
        return None   # still placeholder — skip
    try:
        from langfuse import Langfuse
        return Langfuse(
            public_key=s.langfuse_public_key,
            secret_key=s.langfuse_secret_key,
            host=s.langfuse_host,
        )
    except Exception:
        return None


@contextmanager
def trace(name: str, **metadata):
    """No-op context manager if Langfuse is unavailable."""
    lf = get_langfuse()
    if lf is None:
        yield None
        return
    try:
        # Langfuse v2 uses lf.trace(), v3 uses lf.start_trace() — handle both
        if hasattr(lf, "start_trace"):
            span = lf.start_trace(name=name, metadata=metadata)
        elif hasattr(lf, "trace"):
            span = lf.trace(name=name, metadata=metadata)
        else:
            yield None
            return
        yield span
    except Exception:
        yield None   # tracing error should never crash the request
    finally:
        try:
            lf.flush()
        except Exception:
            pass
