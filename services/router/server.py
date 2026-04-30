"""Tiny FastAPI service: classifies a question as 'fast' (Haiku) or 'smart' (Opus).

Loads a fine-tuned DistilBERT + LoRA adapter if MODEL_DIR exists; otherwise falls back
to a heuristic so the system runs end-to-end without training.
"""
from __future__ import annotations
import os
import re
from functools import lru_cache
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel

# Prometheus metrics for the router
ROUTE_TOTAL  = Counter("router_requests_total", "Total route calls", ["tier", "backend"])
ROUTE_CONF   = Histogram("router_confidence", "Classifier confidence score",
                         buckets=(0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0))

MODEL_DIR = os.getenv("ROUTER_MODEL_DIR", "out/router")

app = FastAPI(title="InsightAgent Router")


class Req(BaseModel):
    question: str


class Resp(BaseModel):
    tier: str         # "fast" | "smart"
    confidence: float
    backend: str      # "model" | "heuristic"


@lru_cache
def _load_model():
    if not os.path.isdir(MODEL_DIR):
        return None
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        tok = AutoTokenizer.from_pretrained(MODEL_DIR)
        mdl = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR).eval()
        return tok, mdl, torch
    except Exception:
        return None


_HARD_HINTS = re.compile(
    r"\b(why|compare|trade.?off|derive|prove|implications?|across|trend|"
    r"summari[sz]e .* and .*|step.?by.?step|reason)\b",
    re.IGNORECASE,
)


def _heuristic(q: str) -> tuple[str, float]:
    if len(q.split()) > 24 or _HARD_HINTS.search(q) or q.count("?") > 1:
        return "smart", 0.7
    return "fast", 0.65


@app.post("/route", response_model=Resp)
def route(r: Req) -> Resp:
    loaded = _load_model()
    if loaded is None:
        tier, conf = _heuristic(r.question)
        ROUTE_TOTAL.labels(tier=tier, backend="heuristic").inc()
        ROUTE_CONF.observe(conf)
        return Resp(tier=tier, confidence=conf, backend="heuristic")
    tok, mdl, torch = loaded
    with torch.no_grad():
        inp = tok(r.question, truncation=True, max_length=128, return_tensors="pt")
        logits = mdl(**inp).logits[0]
        probs = torch.softmax(logits, dim=-1).tolist()
    tier = "smart" if probs[1] >= 0.5 else "fast"
    conf = float(max(probs))
    ROUTE_TOTAL.labels(tier=tier, backend="model").inc()
    ROUTE_CONF.observe(conf)
    return Resp(tier=tier, confidence=conf, backend="model")


@app.get("/health")
def health():
    return {"ok": True, "model_loaded": _load_model() is not None}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
