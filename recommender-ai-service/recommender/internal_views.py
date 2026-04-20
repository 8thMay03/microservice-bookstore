"""
Internal API for graph-rag-service to pull behavior events for ETL into Neo4j.
Only accessible from within the Docker network.
"""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomerBehaviorEvent


class InternalBehaviorEventsView(APIView):
    """
    GET /internal/recommender/behavior-events/

    Returns all behavior events (customer_id, product_id, event_type).
    Used by graph-rag-service to build the knowledge graph in Neo4j.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        events = list(
            CustomerBehaviorEvent.objects.values(
                "customer_id", "product_id", "event_type"
            )
        )
        return Response(events)
