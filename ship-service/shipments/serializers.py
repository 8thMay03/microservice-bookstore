from rest_framework import serializers
from .models import Shipment


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = [
            "id", "order_id", "customer_id", "shipping_address",
            "status", "tracking_number", "carrier", "estimated_delivery",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "tracking_number", "created_at", "updated_at"]


class CreateShipmentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    customer_id = serializers.IntegerField()
    shipping_address = serializers.CharField()
    carrier = serializers.CharField(default="BookStore Logistics")


class UpdateStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Shipment.Status.choices)
