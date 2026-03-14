import logging
from collections import defaultdict
from typing import Dict, List

import requests
from django.conf import settings

from .models import RecommendationCache

logger = logging.getLogger(__name__)


def _fetch_all_orders() -> List[dict]:
  """Lightweight fetch of all completed orders for analytics."""
  try:
    resp = requests.get(
      f"{settings.ORDER_SERVICE_URL}/api/orders/",
      timeout=10,
    )
    resp.raise_for_status()
    orders = resp.json()
    completed = {"PAID", "SHIPPED", "DELIVERED"}
    return [o for o in orders if o.get("status") in completed]
  except requests.RequestException as exc:
    logger.error("analytics: failed to fetch orders: %s", exc)
    return []


def _fetch_book_categories(book_ids: List[int]) -> Dict[int, int]:
  if not book_ids:
    return {}
  try:
    resp = requests.post(
      f"{settings.BOOK_SERVICE_URL}/internal/books/bulk/",
      json={"ids": book_ids},
      timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    return {b["id"]: b.get("category_id") for b in data}
  except requests.RequestException as exc:
    logger.error("analytics: failed to fetch book categories: %s", exc)
    return {}


def build_overview() -> dict:
  """
  Compute:
    - category_purchase_counts: how many items sold per category
    - overall orders/items
    - simple recommendation conversion:
        impressions = number of cached recommendations
        conversions = recommendations where (customer, book) later appears in an order
  """
  orders = _fetch_all_orders()
  if not orders:
    return {
      "total_orders": 0,
      "total_items": 0,
      "category_purchase_counts": {},
      "recommendation_impressions": 0,
      "recommendation_conversions": 0,
      "recommendation_conversion_rate": 0.0,
    }

  total_items = 0
  all_book_ids: List[int] = []
  for o in orders:
    for it in o.get("items", []):
      total_items += it.get("quantity", 1)
      all_book_ids.append(it["book_id"])

  cat_map = _fetch_book_categories(list(set(all_book_ids)))
  cat_counts: Dict[int, int] = defaultdict(int)
  for o in orders:
    for it in o.get("items", []):
      bid = it["book_id"]
      qty = it.get("quantity", 1)
      cat_id = cat_map.get(bid)
      if cat_id is not None:
        cat_counts[cat_id] += qty

  # Recommendation conversion (very approximate)
  impressions = RecommendationCache.objects.count()
  conversions = 0
  if impressions:
    # Build fast lookup of (customer_id, book_id) that were actually purchased.
    purchased_pairs = set()
    for o in orders:
      cid = o.get("customer_id")
      for it in o.get("items", []):
        purchased_pairs.add((cid, it["book_id"]))

    for rec in RecommendationCache.objects.all().only("customer_id", "book_id"):
      if (rec.customer_id, rec.book_id) in purchased_pairs:
        conversions += 1

  rate = (conversions / impressions) if impressions else 0.0

  return {
    "total_orders": len(orders),
    "total_items": total_items,
    "category_purchase_counts": cat_counts,
    "recommendation_impressions": impressions,
    "recommendation_conversions": conversions,
    "recommendation_conversion_rate": round(rate, 4),
  }

