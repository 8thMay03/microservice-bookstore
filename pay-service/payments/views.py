import random
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from .serializers import PaymentSerializer


class PaymentDetailView(APIView):
    """GET /api/payments/<id>/ — retrieve payment details."""

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        return Response(PaymentSerializer(payment).data)


class PaymentByOrderView(APIView):
    """GET /api/payments/order/<order_id>/"""

    def get(self, request, order_id):
        payment = get_object_or_404(Payment, order_id=order_id)
        return Response(PaymentSerializer(payment).data)
