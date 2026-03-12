import uuid
from django.db import models


class Shipment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        DELIVERED = "DELIVERED", "Delivered"
        RETURNED = "RETURNED", "Returned"

    order_id = models.IntegerField(unique=True, help_text="FK to order-service Order")
    customer_id = models.IntegerField(help_text="FK to customer-service Customer")
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    tracking_number = models.UUIDField(default=uuid.uuid4, unique=True)
    carrier = models.CharField(max_length=100, default="BookStore Logistics")
    estimated_delivery = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipments"

    def __str__(self):
        return f"Shipment({self.tracking_number}) — {self.status}"
