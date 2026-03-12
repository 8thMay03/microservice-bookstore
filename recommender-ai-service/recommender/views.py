import requests
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .engine import get_recommendations
from .models import RecommendationCache

logger = logging.getLogger(__name__)


class RecommendationView(APIView):
    """
    GET /api/recommendations/<customer_id>/

    Returns a ranked list of recommended books for a customer.
    Uses collaborative filtering; falls back to popularity-based when
    the customer has insufficient purchase history.
    """

    def get(self, request, customer_id):
        limit = int(request.query_params.get("limit", 10))
        refresh = request.query_params.get("refresh", "false").lower() == "true"

        if not refresh:
            cached = RecommendationCache.objects.filter(
                customer_id=customer_id
            ).order_by("-score")[:limit]
            if cached.exists():
                return Response(self._format_cached(cached))

        # Compute fresh recommendations
        recs = get_recommendations(customer_id, limit)

        # Persist
        RecommendationCache.objects.filter(customer_id=customer_id).delete()
        RecommendationCache.objects.bulk_create([
            RecommendationCache(customer_id=customer_id, book_id=book_id, score=score)
            for book_id, score in recs
        ])

        book_details = self._fetch_book_details([book_id for book_id, _ in recs])
        results = []
        for book_id, score in recs:
            detail = book_details.get(book_id, {})
            results.append({
                "book_id": book_id,
                "score": round(score, 4),
                "title": detail.get("title", ""),
                "author": detail.get("author", ""),
                "price": detail.get("price"),
                "cover_image": detail.get("cover_image", ""),
            })

        return Response({
            "customer_id": customer_id,
            "strategy": "collaborative_filtering",
            "recommendations": results,
        })

    @staticmethod
    def _fetch_book_details(book_ids):
        if not book_ids:
            return {}
        try:
            resp = requests.post(
                f"{settings.BOOK_SERVICE_URL}/internal/books/bulk/",
                json={"ids": book_ids},
                timeout=5,
            )
            resp.raise_for_status()
            return {b["id"]: b for b in resp.json()}
        except requests.RequestException as exc:
            logger.warning("Could not fetch book details: %s", exc)
            return {}

    @staticmethod
    def _format_cached(cached_qs):
        return {
            "customer_id": cached_qs[0].customer_id if cached_qs else None,
            "strategy": "cached",
            "recommendations": [
                {"book_id": r.book_id, "score": round(r.score, 4)}
                for r in cached_qs
            ],
        }
