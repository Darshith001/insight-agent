"""Hybrid retrieval: dense + sparse via Qdrant Query API, fused with RRF, reranked with BGE-reranker."""
from __future__ import annotations
from dataclasses import dataclass
from qdrant_client import models

from services.common.config import get_settings
from services.common.qdrant import get_client, to_sparse_vector
from services.common.embeddings import embed, rerank


@dataclass
class Hit:
    doc_id: str
    chunk_idx: int
    page: int
    section: str
    text: str
    score: float
    source_uri: str


def _hybrid_search(query: str, k: int) -> list[Hit]:
    s = get_settings()
    qc = get_client()
    v = embed([query])
    dense_q = v["dense"][0]
    sparse_q = to_sparse_vector(v["sparse"][0])

    res = qc.query_points(
        collection_name=s.qdrant_collection,
        prefetch=[
            models.Prefetch(query=dense_q, using="dense", limit=k),
            models.Prefetch(query=sparse_q, using="sparse", limit=k),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=k,
        with_payload=True,
    )
    out: list[Hit] = []
    for p in res.points:
        pl = p.payload or {}
        out.append(Hit(
            doc_id=pl.get("doc_id", ""),
            chunk_idx=pl.get("chunk_idx", 0),
            page=pl.get("page", 0),
            section=pl.get("section", ""),
            text=pl.get("text", ""),
            score=float(p.score or 0.0),
            source_uri=pl.get("source_uri", ""),
        ))
    return out


def search(query: str) -> list[Hit]:
    s = get_settings()
    candidates = _hybrid_search(query, s.top_k_retrieve)
    if not candidates:
        return []
    ranked = rerank(query, [c.text for c in candidates], top_k=s.top_k_rerank)
    out: list[Hit] = []
    for idx, score in ranked:
        h = candidates[idx]
        h.score = float(score)
        out.append(h)
    return out


def search_multi(queries: list[str]) -> list[Hit]:
    """Run search per sub-query, dedupe by (doc_id, chunk_idx), keep best score."""
    seen: dict[tuple[str, int], Hit] = {}
    for q in queries:
        for h in search(q):
            key = (h.doc_id, h.chunk_idx)
            if key not in seen or h.score > seen[key].score:
                seen[key] = h
    return sorted(seen.values(), key=lambda x: x.score, reverse=True)[: get_settings().top_k_rerank]
