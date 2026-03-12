import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Payment
from .serializers import PaymentSerializer, ProcessPaymentSerializer


class InternalProcessPaymentView(APIView):
    """Called by order-service to process payment for an order."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProcessPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Idempotency: return existing payment if already processed
        existing = Payment.objects.filter(order_id=data["order_id"]).first()
        if existing:
            return Response(PaymentSerializer(existing).data)

        # Simulate payment gateway (90% success rate in dev)
        payment_success = random.random() < 0.9

        payment = Payment.objects.create(
            order_id=data["order_id"],
            customer_id=data["customer_id"],
            amount=data["amount"],
            method=data["method"],
            status=Payment.Status.COMPLETED if payment_success else Payment.Status.FAILED,
        )
        http_status = status.HTTP_201_CREATED if payment_success else status.HTTP_402_PAYMENT_REQUIRED
        return Response(PaymentSerializer(payment).data, status=http_status)
