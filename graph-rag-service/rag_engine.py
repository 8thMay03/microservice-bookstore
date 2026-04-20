"""
rag_engine.py
=============
Orchestrator that combines:
  1. Graph context  — Neo4j subgraph linearized to text (customer-specific)
  2. Vector context — FAISS hybrid BM25+embedding over store knowledge
  3. LLM generation — Gemini with a personalized system prompt
"""
from __future__ import annotations

import logging
from typing import Optional

import google.generativeai as genai
from decouple import config

from graph_retriever import GraphRetriever
from vector_store import VectorStore

logger = logging.getLogger(__name__)

GOOGLE_API_KEY    = config("GOOGLE_API_KEY",    default="")
GENERATIVE_MODEL  = config("GENERATIVE_MODEL",  default="gemini-2.5-flash")


def _safe_genai_init():
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)


_safe_genai_init()


class GraphRAGEngine:
    """
    Personalized RAG engine.

    Usage:
        engine = GraphRAGEngine()
        reply  = engine.chat("Tôi muốn tìm sách về lập trình", customer_id=3)
        reply  = engine.chat("Gợi ý cho tôi", customer_id=None)  # anonymous
    """

    def __init__(self, knowledge_path: str = "data/knowledge.txt"):
        logger.info("Initializing GraphRAGEngine…")
        self.vector_store    = VectorStore(knowledge_path)
        self.graph_retriever = GraphRetriever()
        logger.info("GraphRAGEngine ready.")

    # ── Prompt builder ────────────────────────────────────────────────────

    @staticmethod
    def _build_prompt(
        user_message: str,
        graph_context: str,
        vector_context: str,
        customer_id: Optional[int],
    ) -> str:
        persona = (
            "Bạn là AI Advisor thân thiện tên **BookBot** của cửa hàng Microservice Bookstore.\n"
            "Nhiệm vụ của bạn là tư vấn mua hàng **cá nhân hóa** dựa trên lịch sử và sở thích của khách.\n"
            "Luôn trả lời bằng tiếng Việt, ngắn gọn và hữu ích.\n"
            "Nếu không có đủ thông tin, hãy nói lịch sự và đề nghị khách gọi Hotline 1900-1234."
        )

        if customer_id:
            personalization_note = (
                f"Khách hàng hiện tại có ID = {customer_id}. "
                "Hãy ưu tiên gợi ý những sản phẩm phù hợp với lịch sử và sở thích của họ."
            )
        else:
            personalization_note = (
                "Khách chưa đăng nhập. Hãy gợi ý những sản phẩm phổ biến và hữu ích chung."
            )

        return f"""{persona}

{personalization_note}

--- DỮ LIỆU ĐỒ THỊ (lịch sử, hành vi, gợi ý cá nhân) ---
{graph_context}

--- TÀI LIỆU CỬA HÀNG (chính sách, danh sách sản phẩm, FAQ) ---
{vector_context}
---

Câu hỏi của khách: {user_message}
BookBot trả lời:"""

    # ── Chat ─────────────────────────────────────────────────────────────

    def chat(
        self,
        user_message: str,
        customer_id: Optional[int] = None,
    ) -> str:
        if not GOOGLE_API_KEY:
            return (
                "Xin lỗi, dịch vụ AI chưa được cấu hình GOOGLE_API_KEY. "
                "Vui lòng liên hệ quản trị viên."
            )

        # 1. Graph retrieval (personalized or trending)
        try:
            if customer_id:
                graph_ctx = self.graph_retriever.get_customer_context(customer_id)
            else:
                graph_ctx = self.graph_retriever.get_anonymous_context()
        except Exception as exc:
            logger.warning("graph retrieval failed (neo4j down?): %s", exc)
            graph_ctx = "(Không thể kết nối đồ thị tri thức)"

        # 2. Vector retrieval (store FAQ + policies + product list)
        try:
            vector_chunks = self.vector_store.search(user_message, top_k=4)
            vector_ctx = "\n\n".join(f"- {c}" for c in vector_chunks)
        except Exception as exc:
            logger.warning("vector retrieval failed: %s", exc)
            vector_ctx = "(Không thể truy xuất tài liệu cửa hàng)"

        # 3. Build prompt
        prompt = self._build_prompt(
            user_message, graph_ctx, vector_ctx, customer_id
        )

        # 4. Generate with Gemini
        try:
            model = genai.GenerativeModel(GENERATIVE_MODEL)
            response = model.generate_content(prompt)
            return response.text
        except Exception as exc:
            logger.error("LLM generation error: %s", exc)
            return (
                f"Xin lỗi, tôi đang gặp sự cố khi kết nối AI ({exc}). "
                "Bạn có thể thử lại sau hoặc gọi Hotline 1900-1234."
            )
