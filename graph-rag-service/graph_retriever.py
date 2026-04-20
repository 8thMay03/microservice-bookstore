"""
graph_retriever.py
==================
Queries the Neo4j knowledge graph to build personalized context text
for a given customer before passing it to the LLM.

Public API
----------
  get_customer_context(customer_id) -> str
      Full linearized context for the customer (used in personalized prompt).

  get_anonymous_context() -> str
      Popular / trending products for unauthenticated users.
"""
from __future__ import annotations

import logging
from typing import Optional

from decouple import config
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

NEO4J_URI      = config("NEO4J_URI",      default="bolt://neo4j:7687")
NEO4J_USER     = config("NEO4J_USER",     default="neo4j")
NEO4J_PASSWORD = config("NEO4J_PASSWORD", default="neo4jpassword123")


class GraphRetriever:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self._driver.close()

    def _run(self, cypher: str, **params):
        with self._driver.session() as session:
            return list(session.run(cypher, **params))

    # ── Customer basic info ───────────────────────────────────────────────

    def _customer_info(self, customer_id: int) -> Optional[dict]:
        rows = self._run(
            "MATCH (c:Customer {id: $cid}) RETURN c.name AS name, c.email AS email",
            cid=customer_id,
        )
        if not rows:
            return None
        return {"name": rows[0]["name"], "email": rows[0]["email"]}

    # ── Purchased products ────────────────────────────────────────────────

    def _purchased_products(self, customer_id: int, limit: int = 10) -> list:
        rows = self._run(
            """
            MATCH (c:Customer {id: $cid})-[r:PURCHASED]->(p:Product)
            OPTIONAL MATCH (p)-[:IN_CATEGORY]->(cat:Category)
            RETURN p.title AS title, p.brand AS brand, p.price AS price,
                   cat.name AS category, r.times AS times
            ORDER BY r.times DESC LIMIT $limit
            """,
            cid=customer_id, limit=limit,
        )
        return [dict(r) for r in rows]

    # ── Favorite categories ────────────────────────────────────────────────

    def _favorite_categories(self, customer_id: int, limit: int = 5) -> list:
        rows = self._run(
            """
            MATCH (c:Customer {id: $cid})-[:PURCHASED|CLICKED|ADDED_TO_CART]->(p:Product)
                  -[:IN_CATEGORY]->(cat:Category)
            RETURN cat.name AS name, count(*) AS score
            ORDER BY score DESC LIMIT $limit
            """,
            cid=customer_id, limit=limit,
        )
        return [r["name"] for r in rows if r["name"]]

    # ── Recent behavior ───────────────────────────────────────────────────

    def _recent_behavior(self, customer_id: int, limit: int = 8) -> list:
        """Returns products the user clicked / add_to_cart but has NOT purchased."""
        rows = self._run(
            """
            MATCH (c:Customer {id: $cid})-[r:CLICKED|ADDED_TO_CART]->(p:Product)
            WHERE NOT (c)-[:PURCHASED]->(p)
            RETURN p.title AS title, p.brand AS brand, p.price AS price,
                   type(r) AS action, r.count AS count
            ORDER BY r.count DESC LIMIT $limit
            """,
            cid=customer_id, limit=limit,
        )
        return [dict(r) for r in rows]

    # ── Category-based recommendations (not yet purchased) ────────────────

    def _category_recommendations(self, customer_id: int, limit: int = 10) -> list:
        rows = self._run(
            """
            MATCH (c:Customer {id: $cid})-[:PURCHASED|CLICKED]->(p:Product)
                  -[:IN_CATEGORY]->(cat:Category)
            WITH c, collect(DISTINCT cat) AS pref_cats
            UNWIND pref_cats AS cat
            MATCH (rec:Product)-[:IN_CATEGORY]->(cat)
            WHERE NOT (c)-[:PURCHASED]->(rec)
            RETURN rec.title AS title, rec.brand AS brand,
                   rec.price AS price, cat.name AS category,
                   count(*) AS relevance
            ORDER BY relevance DESC LIMIT $limit
            """,
            cid=customer_id, limit=limit,
        )
        return [dict(r) for r in rows]

    # ── Collaborative (what similar customers bought) ─────────────────────

    def _collaborative_recommendations(self, customer_id: int, limit: int = 8) -> list:
        rows = self._run(
            """
            MATCH (c:Customer {id: $cid})-[:PURCHASED]->(p:Product)
                  <-[:PURCHASED]-(similar:Customer)
            MATCH (similar)-[:PURCHASED]->(rec:Product)
            WHERE NOT (c)-[:PURCHASED]->(rec) AND rec.id <> p.id
            RETURN rec.title AS title, rec.brand AS brand,
                   rec.price AS price, count(*) AS score
            ORDER BY score DESC LIMIT $limit
            """,
            cid=customer_id, limit=limit,
        )
        return [dict(r) for r in rows]

    # ── Trending (most purchased overall) ────────────────────────────────

    def _trending_products(self, limit: int = 10) -> list:
        rows = self._run(
            """
            MATCH ()-[r:PURCHASED]->(p:Product)
            OPTIONAL MATCH (p)-[:IN_CATEGORY]->(cat:Category)
            RETURN p.title AS title, p.brand AS brand,
                   p.price AS price, cat.name AS category,
                   sum(r.times) AS total_purchases
            ORDER BY total_purchases DESC LIMIT $limit
            """,
            limit=limit,
        )
        return [dict(r) for r in rows]

    # ── Linearizers ──────────────────────────────────────────────────────

    @staticmethod
    def _fmt_product(p: dict) -> str:
        return f"{p.get('title','?')} ({p.get('brand','')}) – ${p.get('price','?')}"

    def get_customer_context(self, customer_id: int) -> str:
        """
        Returns a multi-section text block describing the customer's
        profile, history, and personalised suggestions.
        """
        info = self._customer_info(customer_id)
        if info is None:
            return self.get_anonymous_context()

        lines = [f"=== HỒ SƠ KHÁCH HÀNG (ID: {customer_id}) ==="]
        lines.append(f"Tên: {info['name']}")

        fav_cats = self._favorite_categories(customer_id)
        if fav_cats:
            lines.append(f"Danh mục yêu thích: {', '.join(fav_cats)}")

        purchased = self._purchased_products(customer_id)
        if purchased:
            lines.append("\n[Sản phẩm đã mua gần đây]")
            for p in purchased[:6]:
                lines.append(f"  • {self._fmt_product(p)}")

        behavior = self._recent_behavior(customer_id)
        if behavior:
            lines.append("\n[Đang quan tâm (xem / thêm giỏ nhưng chưa mua)]")
            for p in behavior:
                action_vn = {"CLICKED": "đã click", "ADDED_TO_CART": "đã thêm giỏ"}.get(
                    p.get("action", ""), p.get("action", "")
                )
                lines.append(f"  • {self._fmt_product(p)}  [{action_vn}]")

        cat_recs = self._category_recommendations(customer_id)
        if cat_recs:
            lines.append("\n[Gợi ý theo sở thích danh mục]")
            for p in cat_recs[:6]:
                lines.append(f"  • {self._fmt_product(p)}  (danh mục: {p.get('category','')})")

        collab_recs = self._collaborative_recommendations(customer_id)
        if collab_recs:
            lines.append("\n[Khách tương tự cũng đã mua]")
            for p in collab_recs[:5]:
                lines.append(f"  • {self._fmt_product(p)}")

        return "\n".join(lines)

    def get_anonymous_context(self) -> str:
        """Context block for unauthenticated users — trending products."""
        trending = self._trending_products()
        lines = ["=== SẢN PHẨM PHỔ BIẾN TRONG CỬA HÀNG ==="]
        for p in trending:
            lines.append(f"  • {self._fmt_product(p)}  (danh mục: {p.get('category','')})")
        return "\n".join(lines)
