"""
Recommendation engine.

Strategy 1 — Collaborative Filtering (user-based):
  Build a customer × book purchase matrix from order history.
  Find the k nearest customers using cosine similarity.
  Recommend books those neighbours bought that the target customer hasn't.

Strategy 2 — Popularity Fallback:
  When the target customer has no history, return the most-purchased books overall.
"""
import logging
from collections import defaultdict
from typing import List, Tuple

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _fetch_all_orders() -> List[dict]:
    """Fetch all orders from order-service; we keep only PAID/SHIPPED/DELIVERED for the matrix."""
    try:
        resp = requests.get(
            f"{settings.ORDER_SERVICE_URL}/api/orders/",
            timeout=10,
        )
        resp.raise_for_status()
        orders = resp.json()
        completed = {
            "PAID", "SHIPPED", "DELIVERED",
        }
        return [o for o in orders if o.get("status") in completed]
    except requests.RequestException as exc:
        logger.error("Failed to fetch orders: %s", exc)
        return []


def _fetch_customer_orders(customer_id: int) -> List[dict]:
    try:
        resp = requests.get(
            f"{settings.ORDER_SERVICE_URL}/internal/orders/customer/{customer_id}/history/",
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.error("Failed to fetch orders for customer %s: %s", customer_id, exc)
        return []


def _extract_book_ids_from_orders(orders: List[dict]) -> List[int]:
    book_ids = []
    for order in orders:
        for item in order.get("items", []):
            book_ids.append(item["book_id"])
    return list(set(book_ids))


def popularity_based(limit: int = 10) -> List[Tuple[int, float]]:
    """Return (book_id, score) tuples ranked by purchase frequency."""
    orders = _fetch_all_orders()
    counts: dict = defaultdict(int)
    for order in orders:
        for item in order.get("items", []):
            counts[item["book_id"]] += item.get("quantity", 1)
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    max_count = ranked[0][1] if ranked else 1
    return [(book_id, count / max_count) for book_id, count in ranked]


def collaborative_filtering(customer_id: int, limit: int = 10) -> List[Tuple[int, float]]:
    """User-based collaborative filtering using cosine similarity."""
    try:
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        logger.warning("numpy/sklearn not available; falling back to popularity.")
        return popularity_based(limit)

    # Build customer → set of purchased book_ids
    all_orders = _fetch_all_orders()
    customer_books: dict = defaultdict(set)
    for order in all_orders:
        cid = order.get("customer_id")
        for item in order.get("items", []):
            customer_books[cid].add(item["book_id"])

    if not customer_books:
        return popularity_based(limit)

    all_book_ids = sorted({b for books in customer_books.values() for b in books})
    if not all_book_ids:
        return popularity_based(limit)

    book_index = {b: i for i, b in enumerate(all_book_ids)}
    customer_ids = sorted(customer_books.keys())
    customer_index = {c: i for i, c in enumerate(customer_ids)}

    matrix = np.zeros((len(customer_ids), len(all_book_ids)), dtype=np.float32)
    for cid, books in customer_books.items():
        for book in books:
            matrix[customer_index[cid], book_index[book]] = 1.0

    if customer_id not in customer_index:
        return popularity_based(limit)

    target_vec = matrix[customer_index[customer_id]].reshape(1, -1)
    similarities = cosine_similarity(target_vec, matrix)[0]
    already_purchased = customer_books[customer_id]

    candidate_scores: dict = defaultdict(float)
    for i, sim in enumerate(similarities):
        if customer_ids[i] == customer_id or sim <= 0:
            continue
        for book_id in customer_books[customer_ids[i]]:
            if book_id not in already_purchased:
                candidate_scores[book_id] += sim

    if not candidate_scores:
        return popularity_based(limit)

    ranked = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
    max_score = ranked[0][1] if ranked else 1
    return [(book_id, score / max_score) for book_id, score in ranked]


def get_recommendations(customer_id: int, limit: int = 10) -> List[Tuple[int, float]]:
    results = collaborative_filtering(customer_id, limit)
    if not results:
        results = popularity_based(limit)
    return results
