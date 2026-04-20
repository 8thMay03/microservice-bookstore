"""
graph_builder.py
================
ETL pipeline: pulls data from every microservice and upserts into Neo4j.

Graph schema
------------
Nodes:
  (:Customer  {id, name, email})
  (:Product   {id, title, brand, price, product_type, sku, description})
  (:Category  {id, name, slug})

Relationships:
  (:Customer)-[:PURCHASED  {times}]->(:Product)   # from completed orders
  (:Customer)-[:VIEWED     {count}]->(:Product)   # from behavior events
  (:Customer)-[:CLICKED    {count}]->(:Product)   # from behavior events
  (:Customer)-[:ADDED_TO_CART {count}]->(:Product)
  (:Product)-[:IN_CATEGORY]->(:Category)
  (:Category)-[:PARENT_OF]->(:Category)           # subcategory hierarchy
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

import requests
from decouple import config
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

# ── Service URLs (injected via docker-compose env) ─────────────────────────
ORDER_SERVICE_URL       = config("ORDER_SERVICE_URL",       default="http://order-service:8000")
PRODUCT_SERVICE_URL     = config("PRODUCT_SERVICE_URL",     default="http://product-service:8000")
CATALOG_SERVICE_URL     = config("CATALOG_SERVICE_URL",     default="http://catalog-service:8000")
CUSTOMER_SERVICE_URL    = config("CUSTOMER_SERVICE_URL",    default="http://customer-service:8000")
RECOMMENDER_SERVICE_URL = config("RECOMMENDER_SERVICE_URL", default="http://recommender-ai-service:8000")

NEO4J_URI      = config("NEO4J_URI",      default="bolt://neo4j:7687")
NEO4J_USER     = config("NEO4J_USER",     default="neo4j")
NEO4J_PASSWORD = config("NEO4J_PASSWORD", default="neo4jpassword123")

COMPLETED_STATUSES = {"PAID", "SHIPPED", "DELIVERED"}
_TIMEOUT = 10


# ── HTTP helpers ────────────────────────────────────────────────────────────

def _get(url: str, params: Optional[dict] = None) -> Optional[Any]:
    try:
        r = requests.get(url, params=params, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        logger.warning("graph_builder GET %s failed: %s", url, exc)
        return None


def _post(url: str, body: dict) -> Optional[Any]:
    try:
        r = requests.post(url, json=body, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        logger.warning("graph_builder POST %s failed: %s", url, exc)
        return None


# ── Data fetchers ───────────────────────────────────────────────────────────

def fetch_products() -> List[dict]:
    data = _get(f"{PRODUCT_SERVICE_URL}/api/products/")
    if not data:
        return []
    return data if isinstance(data, list) else data.get("results", [])


def fetch_categories() -> List[dict]:
    data = _get(f"{CATALOG_SERVICE_URL}/api/catalog/categories/")
    if not data:
        return []
    return data if isinstance(data, list) else data.get("results", [])


def fetch_customers() -> List[dict]:
    data = _get(f"{CUSTOMER_SERVICE_URL}/api/customers/")
    if not data:
        return []
    return data if isinstance(data, list) else data.get("results", [])


def fetch_orders() -> List[dict]:
    data = _get(f"{ORDER_SERVICE_URL}/api/orders/")
    if not data:
        return []
    orders = data if isinstance(data, list) else data.get("results", [])
    return [o for o in orders if o.get("status") in COMPLETED_STATUSES]


def fetch_behavior_events() -> List[dict]:
    """Call internal API on recommender-ai-service."""
    data = _get(f"{RECOMMENDER_SERVICE_URL}/internal/recommender/behavior-events/")
    if not data:
        return []
    return data if isinstance(data, list) else data.get("results", [])


# ── Neo4j builder ───────────────────────────────────────────────────────────

class GraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def _run(self, cypher: str, **params):
        with self.driver.session() as session:
            session.run(cypher, **params)

    # ── Constraint / index setup ─────────────────────────────────────────

    def setup_schema(self):
        constraints = [
            "CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT product_id  IF NOT EXISTS FOR (p:Product)  REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT category_id IF NOT EXISTS FOR (cat:Category) REQUIRE cat.id IS UNIQUE",
        ]
        with self.driver.session() as session:
            for c in constraints:
                try:
                    session.run(c)
                except Exception as exc:
                    logger.debug("schema: %s", exc)
        logger.info("graph schema constraints ready")

    # ── Node upserts ─────────────────────────────────────────────────────

    def upsert_categories(self, categories: List[dict]):
        cypher = """
        UNWIND $rows AS row
        MERGE (c:Category {id: row.id})
        SET c.name = row.name,
            c.slug = row.slug
        """
        rows = [
            {"id": int(cat["id"]), "name": cat.get("name", ""), "slug": cat.get("slug", "")}
            for cat in categories
            if cat.get("id") is not None
        ]
        if rows:
            self._run(cypher, rows=rows)
            logger.info("upserted %d categories", len(rows))

        # Parent-of relationships
        parent_cypher = """
        UNWIND $rows AS row
        MATCH (child:Category {id: row.child_id})
        MATCH (parent:Category {id: row.parent_id})
        MERGE (parent)-[:PARENT_OF]->(child)
        """
        parent_rows = [
            {"child_id": int(cat["id"]), "parent_id": int(cat["parent"])}
            for cat in categories
            if cat.get("parent") is not None and cat.get("id") is not None
        ]
        if parent_rows:
            self._run(parent_cypher, rows=parent_rows)

    def upsert_products(self, products: List[dict]):
        cypher = """
        UNWIND $rows AS row
        MERGE (p:Product {id: row.id})
        SET p.title        = row.title,
            p.brand        = row.brand,
            p.price        = row.price,
            p.product_type = row.product_type,
            p.sku          = row.sku,
            p.description  = row.description
        WITH p, row
        WHERE row.category_id IS NOT NULL
        MATCH (cat:Category {id: row.category_id})
        MERGE (p)-[:IN_CATEGORY]->(cat)
        """
        rows = []
        for p in products:
            if p.get("id") is None:
                continue
            rows.append({
                "id":           int(p["id"]),
                "title":        p.get("title", ""),
                "brand":        p.get("brand", ""),
                "price":        float(p.get("price", 0)),
                "product_type": p.get("product_type", ""),
                "sku":          p.get("sku", ""),
                "description":  p.get("description", ""),
                "category_id":  int(p["category_id"]) if p.get("category_id") else None,
            })
        if rows:
            self._run(cypher, rows=rows)
            logger.info("upserted %d products", len(rows))

    def upsert_customers(self, customers: List[dict]):
        cypher = """
        UNWIND $rows AS row
        MERGE (c:Customer {id: row.id})
        SET c.name  = row.name,
            c.email = row.email
        """
        rows = [
            {
                "id":    int(c["id"]),
                "name":  f"{c.get('first_name', '')} {c.get('last_name', '')}".strip(),
                "email": c.get("email", ""),
            }
            for c in customers
            if c.get("id") is not None
        ]
        if rows:
            self._run(cypher, rows=rows)
            logger.info("upserted %d customers", len(rows))

    # ── Relationship upserts ──────────────────────────────────────────────

    def upsert_purchase_edges(self, orders: List[dict]):
        """Aggregate completed-order items into PURCHASED(times) edges."""
        purchase_counts: Dict[tuple, int] = defaultdict(int)
        for order in orders:
            cid = order.get("customer_id")
            if cid is None:
                continue
            for item in order.get("items", []):
                pid = item.get("product_id")
                if pid is not None:
                    purchase_counts[(int(cid), int(pid))] += 1

        cypher = """
        UNWIND $rows AS row
        MATCH (c:Customer {id: row.cid})
        MATCH (p:Product  {id: row.pid})
        MERGE (c)-[r:PURCHASED]->(p)
        SET r.times = row.times
        """
        rows = [{"cid": cid, "pid": pid, "times": t}
                for (cid, pid), t in purchase_counts.items()]
        if rows:
            self._run(cypher, rows=rows)
            logger.info("upserted %d PURCHASED edges", len(rows))

    def upsert_behavior_edges(self, events: List[dict]):
        """Aggregate view/click/add_to_cart events into weighted edges."""
        # {(cid, pid, event_type): count}
        counts: Dict[tuple, int] = defaultdict(int)
        for ev in events:
            try:
                cid = int(ev["customer_id"])
                pid = int(ev["product_id"])
                et  = str(ev.get("event_type", "")).strip().lower()
            except (KeyError, TypeError, ValueError):
                continue
            if et in ("view", "click", "add_to_cart"):
                counts[(cid, pid, et)] += 1

        # map event_type → relationship type
        rel_map = {
            "view":         "VIEWED",
            "click":        "CLICKED",
            "add_to_cart":  "ADDED_TO_CART",
        }
        for event_type, rel_type in rel_map.items():
            rows = [
                {"cid": cid, "pid": pid, "count": cnt}
                for (cid, pid, et), cnt in counts.items()
                if et == event_type
            ]
            if not rows:
                continue
            cypher = f"""
            UNWIND $rows AS row
            MATCH (c:Customer {{id: row.cid}})
            MATCH (p:Product  {{id: row.pid}})
            MERGE (c)-[r:{rel_type}]->(p)
            SET r.count = row.count
            """
            self._run(cypher, rows=rows)
            logger.info("upserted %d %s edges", len(rows), rel_type)

    # ── Full sync ─────────────────────────────────────────────────────────

    def full_sync(self) -> Dict[str, int]:
        self.setup_schema()

        categories = fetch_categories()
        products   = fetch_products()
        customers  = fetch_customers()
        orders     = fetch_orders()
        events     = fetch_behavior_events()

        self.upsert_categories(categories)
        self.upsert_products(products)
        self.upsert_customers(customers)
        self.upsert_purchase_edges(orders)
        self.upsert_behavior_edges(events)

        summary = {
            "categories": len(categories),
            "products":   len(products),
            "customers":  len(customers),
            "orders":     len(orders),
            "events":     len(events),
        }
        logger.info("graph full_sync done: %s", summary)
        return summary
