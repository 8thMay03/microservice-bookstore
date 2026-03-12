from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Order
from .serializers import OrderSerializer


class InternalOrderHistoryView(APIView):
    """Called by recommender-ai-service to build recommendation model."""
    permission_classes = [AllowAny]

    def get(self, request, customer_id):
        orders = Order.objects.prefetch_related("items").filter(
            customer_id=customer_id,
            status__in=[Order.Status.PAID, Order.Status.SHIPPED, Order.Status.DELIVERED],
        )
        return Response(OrderSerializer(orders, many=True).data)
