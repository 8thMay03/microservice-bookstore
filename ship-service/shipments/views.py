from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Shipment
from .serializers import ShipmentSerializer, UpdateStatusSerializer


class ShipmentDetailView(APIView):
    """GET /api/shipments/<id>/"""

    def get(self, request, pk):
        shipment = get_object_or_404(Shipment, pk=pk)
        return Response(ShipmentSerializer(shipment).data)


class ShipmentByOrderView(APIView):
    """GET /api/shipments/order/<order_id>/"""

    def get(self, request, order_id):
        shipment = get_object_or_404(Shipment, order_id=order_id)
        return Response(ShipmentSerializer(shipment).data)


class ShipmentStatusView(APIView):
    """PATCH /api/shipments/<id>/status/ — update shipment status."""

    def patch(self, request, pk):
        shipment = get_object_or_404(Shipment, pk=pk)
        serializer = UpdateStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        shipment.status = serializer.validated_data["status"]
        shipment.save()
        return Response(ShipmentSerializer(shipment).data)


class TrackShipmentView(APIView):
    """GET /api/shipments/track/<tracking_number>/"""

    def get(self, request, tracking_number):
        shipment = get_object_or_404(Shipment, tracking_number=tracking_number)
        return Response(ShipmentSerializer(shipment).data)
