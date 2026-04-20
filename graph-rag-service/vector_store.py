"""
vector_store.py
===============
FAISS + Gemini embedding vector store for store knowledge (FAQ, policies,
product descriptions).  Provides hybrid BM25 + vector retrieval identical
to the original rag-service, but as a reusable class.
"""
from __future__ import annotations

import logging
import os
from typing import List, Optional

import numpy as np
import faiss
from rank_bm25 import BM25Okapi
import google.generativeai as genai
from decouple import config

logger = logging.getLogger(__name__)

GOOGLE_API_KEY  = config("GOOGLE_API_KEY", default="")
EMBEDDING_MODEL = "models/embedding-001"


class VectorStore:
    """
    Loads text chunks from a knowledge file, embeds them with Gemini,
    and exposes hybrid BM25 + vector search.
    """

    def __init__(self, data_path: str = "data/knowledge.txt"):
        self.documents: List[str] = []
        self.bm25_index: Optional[BM25Okapi] = None
        self.faiss_index = None
        self._embeddings: Optional[np.ndarray] = None

        if not GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY not set — VectorStore will not embed.")
            return

        genai.configure(api_key=GOOGLE_API_KEY)

        if os.path.exists(data_path):
            self._load(data_path)
        else:
            logger.warning("knowledge file not found: %s", data_path)

    # ── Loading ───────────────────────────────────────────────────────────

    def _chunk(self, text: str, size: int = 400, overlap: int = 50) -> List[str]:
        chunks, start = [], 0
        while start < len(text):
            chunks.append(text[start: start + size])
            start += size - overlap
        return chunks

    def _load(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        raw: List[str] = []
        for block in content.split("==="):
            if block.strip():
                raw.extend(self._chunk(block.strip()))

        self.documents = raw
        logger.info("VectorStore: loaded %d chunks from %s", len(raw), path)

        # BM25
        corpus = [doc.lower().split() for doc in self.documents]
        self.bm25_index = BM25Okapi(corpus)

        # FAISS
        try:
            resp = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=self.documents,
                task_type="retrieval_document",
            )
            emb_list = resp.get("embedding", resp.get("embeddings", []))
            self._embeddings = np.array(emb_list, dtype="float32")
            dim = self._embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dim)
            self.faiss_index.add(self._embeddings)
            logger.info("VectorStore: FAISS index built (%d vectors, dim=%d)", len(self.documents), dim)
        except Exception as exc:
            logger.error("VectorStore: FAISS build failed: %s", exc)

    # ── Query ─────────────────────────────────────────────────────────────

    def _embed_query(self, text: str) -> Optional[np.ndarray]:
        try:
            resp = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_query",
            )
            emb = resp.get("embedding", resp.get("embeddings", []))
            return np.array(emb, dtype="float32").reshape(1, -1)
        except Exception as exc:
            logger.warning("VectorStore: embed query failed: %s", exc)
            return None

    def search(self, query: str, top_k: int = 4) -> List[str]:
        """Hybrid RRF: BM25 + FAISS → top-k document chunks."""
        if not self.documents:
            return []

        # FAISS scores
        faiss_scores: dict = {}
        q_emb = self._embed_query(query)
        if q_emb is not None and self.faiss_index is not None:
            _, indices = self.faiss_index.search(q_emb, len(self.documents))
            for rank, idx in enumerate(indices[0]):
                faiss_scores[idx] = 1.0 / (rank + 60)

        # BM25 scores
        bm25_scores: dict = {}
        if self.bm25_index:
            doc_scores = self.bm25_index.get_scores(query.lower().split())
            for rank, idx in enumerate(np.argsort(doc_scores)[::-1]):
                bm25_scores[int(idx)] = 1.0 / (rank + 60)

        # RRF merge
        final = {i: faiss_scores.get(i, 0) + bm25_scores.get(i, 0)
                 for i in range(len(self.documents))}
        top_indices = sorted(final, key=lambda x: final[x], reverse=True)[:top_k]
        return [self.documents[i] for i in top_indices]
