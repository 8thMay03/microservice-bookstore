"""
Graph RAG Service
=================
FastAPI application that serves a personalized knowledge-graph–powered
RAG chatbot.  Integrates with Neo4j (graph) + FAISS (vector) + Gemini (LLM).

Endpoints
---------
GET  /health                   — liveness probe
GET  /admin/                   — gateway health ping
POST /api/graph-rag/chat       — personalized chat
POST /api/graph-rag/sync       — trigger ETL sync of all services → Neo4j
GET  /api/graph-rag/graph-info — read-only customer graph snapshot
"""
from __future__ import annotations

import logging
from typing import Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph_builder import GraphBuilder
from rag_engine import GraphRAGEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Graph RAG Service — Microservice Bookstore",
    description="Personalized RAG chatbot using Neo4j knowledge graph + FAISS + Gemini.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────────────────────────────────

engine: Optional[GraphRAGEngine] = None
builder: Optional[GraphBuilder] = None


@app.on_event("startup")
async def startup_event():
    global engine, builder
    logger.info("Starting up Graph RAG Service…")
    engine = GraphRAGEngine()
    builder = GraphBuilder()

    # Run initial ETL sync in the background so startup is not blocked.
    logger.info("Scheduling initial graph sync…")
    try:
        builder.full_sync()
        logger.info("Initial graph sync complete.")
    except Exception as exc:
        logger.warning("Initial graph sync failed (Neo4j may not be ready): %s", exc)


@app.on_event("shutdown")
def shutdown_event():
    if builder:
        builder.close()
    if engine:
        engine.graph_retriever.close()


# ── Request / Response models ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str
    customer_id: Optional[int] = None
    personalized: bool = False


class SyncResponse(BaseModel):
    status: str
    summary: dict


class GraphInfoRequest(BaseModel):
    customer_id: int


# ── Endpoints ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "graph-rag-service"}


@app.get("/admin/")
def admin_health():
    """Django-style health check for api-gateway ping."""
    return {"status": "ok", "service": "graph-rag-service"}


@app.post("/api/graph-rag/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Personalized RAG chat.

    Pass `customer_id` to enable graph-based personalization; omit (or null)
    for anonymous users who get trending-product context instead.
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized yet.")
    try:
        reply = engine.chat(request.message, customer_id=request.customer_id)
        return ChatResponse(
            reply=reply,
            customer_id=request.customer_id,
            personalized=request.customer_id is not None,
        )
    except Exception as exc:
        logger.error("chat error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/graph-rag/sync", response_model=SyncResponse)
async def sync_graph(background_tasks: BackgroundTasks):
    """
    Trigger a full ETL sync of all microservices into Neo4j.
    The sync runs in the background; the response returns immediately.
    """
    if builder is None:
        raise HTTPException(status_code=503, detail="Builder not initialized.")

    def _do_sync():
        try:
            summary = builder.full_sync()
            logger.info("Manual sync done: %s", summary)
        except Exception as exc:
            logger.error("Manual sync error: %s", exc)

    background_tasks.add_task(_do_sync)
    return SyncResponse(status="sync_started", summary={})


@app.get("/api/graph-rag/graph-info")
async def graph_info(customer_id: int):
    """
    Returns a structured JSON snapshot of the customer's graph context
    (for debugging / frontend display).
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized.")
    try:
        gr = engine.graph_retriever
        return {
            "customer_id":  customer_id,
            "context_text": gr.get_customer_context(customer_id),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
