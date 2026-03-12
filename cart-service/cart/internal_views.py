from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart
from .serializers import CartSerializer


class InternalCreateCartView(APIView):
    """Called by customer-service on registration."""
    permission_classes = [AllowAny]

    def post(self, request):
        customer_id = request.data.get("customer_id")
        if not customer_id:
            return Response({"error": "customer_id required"}, status=status.HTTP_400_BAD_REQUEST)
        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class InternalCartDetailView(APIView):
    """Called by order-service to snapshot cart contents."""
    permission_classes = [AllowAny]

    def get(self, request, customer_id):
        cart = get_object_or_404(Cart.objects.prefetch_related("items"), customer_id=customer_id)
        return Response(CartSerializer(cart).data)
