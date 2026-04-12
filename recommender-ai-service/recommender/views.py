import requests
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .engine import get_recommendations, item_based_similar
from .models import RecommendationCache
from .analytics import build_overview

logger = logging.getLogger(__name__)


class RecommendationView(APIView):
    """
    GET /api/recommendations/<customer_id>/

    Returns a ranked list of recommended products for a customer.
    Uses behavior_dl (Neural CF) when a trained checkpoint exists; otherwise
    collaborative filtering; then popularity for cold users.
    """

    def get(self, request, customer_id):
        limit = int(request.query_params.get("limit", 10))
        refresh = request.query_params.get("refresh", "false").lower() == "true"

        if not refresh:
            cached = list(
                RecommendationCache.objects.filter(
                    customer_id=customer_id
                ).order_by("-score").values_list("product_id", "score")[:limit]
            )
            if cached:
                product_details = self._fetch_product_details([pid for pid, _ in cached])
                results = []
                for product_id, score in cached:
                    detail = product_details.get(product_id, {})
                    results.append({
                        "product_id": product_id,
                        "score": round(score, 4),
                        "title": detail.get("title", ""),
                        "brand": detail.get("brand", ""),
                        "price": detail.get("price"),
                        "cover_image": detail.get("cover_image", ""),
                        "category_id": detail.get("category_id"),
                        "product_type": detail.get("product_type", ""),
                    })
                return Response({
                    "customer_id": customer_id,
                    "strategy": "cached",
                    "recommendations": results,
                })

        # Compute fresh recommendations
        recs, strategy = get_recommendations(customer_id, limit)

        # Persist
        RecommendationCache.objects.filter(customer_id=customer_id).delete()
        RecommendationCache.objects.bulk_create([
            RecommendationCache(
                customer_id=customer_id,
                product_id=product_id,
                score=score,
                strategy=strategy,
            )
            for product_id, score in recs
        ])

        product_details = self._fetch_product_details([product_id for product_id, _ in recs])
        results = []
        for product_id, score in recs:
            detail = product_details.get(product_id, {})
            results.append({
                "product_id": product_id,
                "score": round(score, 4),
                "title": detail.get("title", ""),
                "brand": detail.get("brand", ""),
                "price": detail.get("price"),
                "cover_image": detail.get("cover_image", ""),
                "category_id": detail.get("category_id"),
                "product_type": detail.get("product_type", ""),
            })

        return Response({
            "customer_id": customer_id,
            "strategy": strategy,
            "recommendations": results,
        })

    @staticmethod
    def _fetch_product_details(product_ids):
        if not product_ids:
            return {}
        try:
            resp = requests.post(
                f"{settings.PRODUCT_SERVICE_URL}/internal/products/bulk/",
                json={"ids": product_ids},
                timeout=5,
            )
            resp.raise_for_status()
            return {p["id"]: p for p in resp.json()}
        except requests.RequestException as exc:
            logger.warning("Could not fetch product details: %s", exc)
            return {}


class ItemRecommendationView(APIView):
    """
    GET /api/recommendations/item/<product_id>/

    \"Because you viewed X, you might like Y\" style suggestions.
    """

    def get(self, request, product_id):
        limit = int(request.query_params.get("limit", 8))
        recs = item_based_similar(product_id, limit)
        product_details = RecommendationView._fetch_product_details([pid for pid, _ in recs])
        results = []
        for pid, score in recs:
            detail = product_details.get(pid, {})
            results.append(
                {
                    "product_id": pid,
                    "score": round(score, 4),
                    "title": detail.get("title", ""),
                    "brand": detail.get("brand", ""),
                    "price": detail.get("price"),
                    "cover_image": detail.get("cover_image", ""),
                    "category_id": detail.get("category_id"),
                    "product_type": detail.get("product_type", ""),
                }
            )
        return Response(
            {
                "product_id": product_id,
                "recommendations": results,
            }
        )


class AnalyticsOverviewView(APIView):
    """
    GET /api/recommendations/analytics/overview/

    Lightweight analytics for admin/marketing dashboards.
    """

    def get(self, request):
        data = build_overview()
        return Response(data, status=status.HTTP_200_OK)
