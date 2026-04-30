from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import chat, ingest
from .metrics import metrics_response
from .auth import issue_token

app = FastAPI(title="InsightAgent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, tags=["chat"])
app.include_router(ingest.router, tags=["ingest"])


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/auth/dev-token")
def dev_token(sub: str = "demo-user"):
    return {"token": issue_token(sub)}


@app.get("/metrics")
def metrics():
    return metrics_response()
