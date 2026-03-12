from django.db import models
from django.core.validators import MinValueValidator


class Book(models.Model):
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cover_image = models.URLField(blank=True)
    category_id = models.IntegerField(help_text="FK to catalog-service Category")
    published_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=50, default="English")
    pages = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.author}"


class BookInventory(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name="inventory")
    stock_quantity = models.PositiveIntegerField(default=0)
    warehouse_location = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "book_inventory"
        verbose_name_plural = "book inventories"

    def __str__(self):
        return f"Inventory for {self.book.title}: {self.stock_quantity}"
