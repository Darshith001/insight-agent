from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

QUERIES = Counter("insight_queries_total", "Total chat queries", ["tier", "cache"])
LATENCY = Histogram("insight_query_latency_seconds", "End-to-end query latency", ["tier"])
CRITIQUE = Histogram("insight_critique_score", "Critic score per query", buckets=(0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0))


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
