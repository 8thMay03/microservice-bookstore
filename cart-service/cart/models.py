from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Cart(models.Model):
    customer_id = models.IntegerField(unique=True, help_text="FK to customer-service Customer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        return f"Cart(customer_id={self.customer_id})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book_id = models.IntegerField(help_text="FK to book-service Book")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        unique_together = ("cart", "book_id")

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"CartItem(book_id={self.book_id}, qty={self.quantity})"
