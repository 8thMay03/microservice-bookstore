from rest_framework import serializers
from .models import Book, BookInventory


class BookInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInventory
        fields = ["stock_quantity", "warehouse_location", "updated_at"]


class BookSerializer(serializers.ModelSerializer):
    inventory = BookInventorySerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "isbn", "description", "price",
            "cover_image", "category_id", "published_date", "language",
            "pages", "is_active", "inventory", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BookWriteSerializer(serializers.ModelSerializer):
    stock_quantity = serializers.IntegerField(write_only=True, default=0)
    warehouse_location = serializers.CharField(write_only=True, default="", allow_blank=True)

    class Meta:
        model = Book
        fields = [
            "title", "author", "isbn", "description", "price",
            "cover_image", "category_id", "published_date", "language",
            "pages", "is_active", "stock_quantity", "warehouse_location",
        ]

    def create(self, validated_data):
        stock_quantity = validated_data.pop("stock_quantity", 0)
        warehouse_location = validated_data.pop("warehouse_location", "")
        book = Book.objects.create(**validated_data)
        BookInventory.objects.create(
            book=book,
            stock_quantity=stock_quantity,
            warehouse_location=warehouse_location,
        )
        return book

    def update(self, instance, validated_data):
        stock_quantity = validated_data.pop("stock_quantity", None)
        warehouse_location = validated_data.pop("warehouse_location", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if stock_quantity is not None or warehouse_location is not None:
            inv, _ = BookInventory.objects.get_or_create(book=instance)
            if stock_quantity is not None:
                inv.stock_quantity = stock_quantity
            if warehouse_location is not None:
                inv.warehouse_location = warehouse_location
            inv.save()
        return instance


class InventoryUpdateSerializer(serializers.Serializer):
    delta = serializers.IntegerField(help_text="Positive to add stock, negative to reduce.")

    def validate_delta(self, value):
        return value
