from django.contrib import admin
from .models import Book, BookInventory


class InventoryInline(admin.TabularInline):
    model = BookInventory
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "isbn", "price", "is_active"]
    search_fields = ["title", "author", "isbn"]
    list_filter = ["is_active", "category_id"]
    inlines = [InventoryInline]
