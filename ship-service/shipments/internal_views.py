from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Shipment
from .serializers import ShipmentSerializer, CreateShipmentSerializer


class InternalCreateShipmentView(APIView):
    """Called by order-service after successful payment."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateShipmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        existing = Shipment.objects.filter(order_id=data["order_id"]).first()
        if existing:
            return Response(ShipmentSerializer(existing).data)

        shipment = Shipment.objects.create(
            order_id=data["order_id"],
            customer_id=data["customer_id"],
            shipping_address=data["shipping_address"],
            carrier=data.get("carrier", "BookStore Logistics"),
            estimated_delivery=date.today() + timedelta(days=5),
        )
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)
