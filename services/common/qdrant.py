"""Qdrant client + collection bootstrap with hybrid (dense + sparse) vectors."""
from __future__ import annotations
from functools import lru_cache
from qdrant_client import QdrantClient, models
from .config import get_settings

DENSE_DIM = 1024  # bge-m3


@lru_cache
def get_client() -> QdrantClient:
    s = get_settings()
    return QdrantClient(
        url=s.qdrant_url,
        api_key=s.qdrant_api_key or None,   # None = unauthenticated (local)
        check_compatibility=False,
        timeout=120,
    )


def ensure_collection() -> None:
    s = get_settings()
    qc = get_client()
    if qc.collection_exists(s.qdrant_collection):
        return
    qc.create_collection(
        collection_name=s.qdrant_collection,
        vectors_config={"dense": models.VectorParams(size=DENSE_DIM, distance=models.Distance.COSINE)},
        sparse_vectors_config={"sparse": models.SparseVectorParams(index=models.SparseIndexParams())},
    )


def to_sparse_vector(weights: dict) -> models.SparseVector:
    return models.SparseVector(
        indices=[int(k) for k in weights.keys()],
        values=[float(v) for v in weights.values()],
    )


def list_documents() -> list[dict]:
    """Return distinct documents stored in Qdrant with chunk counts."""
    s = get_settings()
    qc = get_client()
    seen: dict[str, dict] = {}
    offset = None
    while True:
        result, offset = qc.scroll(
            collection_name=s.qdrant_collection,
            limit=1000,
            with_payload=["doc_id", "source_uri"],
            with_vectors=False,
            offset=offset,
        )
        for pt in result:
            did = (pt.payload or {}).get("doc_id", "unknown")
            if did not in seen:
                seen[did] = {
                    "doc_id": did,
                    "chunks": 0,
                    "source_uri": (pt.payload or {}).get("source_uri", ""),
                }
            seen[did]["chunks"] += 1
        if offset is None:
            break
    return list(seen.values())


def delete_document(doc_id: str) -> bool:
    """Delete all vectors belonging to a doc_id."""
    s = get_settings()
    qc = get_client()
    qc.delete(
        collection_name=s.qdrant_collection,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="doc_id", match=models.MatchValue(value=doc_id)
                    )
                ]
            )
        ),
    )
    return True
