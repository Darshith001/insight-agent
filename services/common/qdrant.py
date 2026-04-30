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
