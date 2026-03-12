from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "order_id", "customer_id", "amount",
            "status", "method", "transaction_id", "created_at",
        ]
        read_only_fields = ["id", "transaction_id", "status", "created_at"]


class ProcessPaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    customer_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    method = serializers.ChoiceField(choices=Payment.Method.choices, default=Payment.Method.CREDIT_CARD)
