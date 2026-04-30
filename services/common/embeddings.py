"""Lazy-loaded BGE-M3 embedder (dense + sparse) + cross-encoder reranker."""
from __future__ import annotations
from functools import lru_cache
from .config import get_settings


@lru_cache
def get_embedder():
    from FlagEmbedding import BGEM3FlagModel
    return BGEM3FlagModel(get_settings().embed_model, use_fp16=False)


def embed(texts: list[str]) -> dict:
    """Returns {'dense': [[...]], 'sparse': [{token_id: weight}, ...]}."""
    out = get_embedder().encode(
        texts, return_dense=True, return_sparse=True, return_colbert_vecs=False
    )
    return {"dense": out["dense_vecs"].tolist(), "sparse": out["lexical_weights"]}


@lru_cache
def get_reranker():
    """Load reranker — falls back gracefully if BGE-reranker is incompatible."""
    try:
        from FlagEmbedding import FlagReranker
        return FlagReranker(get_settings().rerank_model, use_fp16=False, use_bf16=False)
    except Exception:
        return None


def rerank(query: str, docs: list[str], top_k: int = 8) -> list[tuple[int, float]]:
    """Rerank docs. Falls back to score=1.0 passthrough if reranker unavailable."""
    if not docs:
        return []

    reranker = get_reranker()
    if reranker is None:
        # no reranker available — return original order with dummy scores
        return [(i, 1.0 - i * 0.01) for i in range(min(top_k, len(docs)))]

    try:
        pairs = [[query, d] for d in docs]
        scores = reranker.compute_score(pairs, normalize=True)
        if isinstance(scores, float):
            scores = [scores]
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
    except Exception:
        # reranker failed at runtime — fall back to original order
        return [(i, 1.0 - i * 0.01) for i in range(min(top_k, len(docs)))]
