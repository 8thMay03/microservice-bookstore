from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Book, BookInventory
from .serializers import BookSerializer, BookWriteSerializer, InventoryUpdateSerializer


class BookListView(APIView):
    """GET /api/books/ — list books with optional filters."""

    def get(self, request):
        qs = Book.objects.select_related("inventory").filter(is_active=True)
        category_id = request.query_params.get("category_id")
        search = request.query_params.get("search")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        if category_id:
            qs = qs.filter(category_id=category_id)
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(author__icontains=search)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        page = int(request.query_params.get("page", 1))
        page_size = 20
        start = (page - 1) * page_size
        end = start + page_size
        total = qs.count()
        books = qs[start:end]
        return Response({
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": BookSerializer(books, many=True).data,
        })

    def post(self, request):
        serializer = BookWriteSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView(APIView):
    """GET/PUT/DELETE /api/books/<id>/"""

    def get(self, request, pk):
        book = get_object_or_404(Book.objects.select_related("inventory"), pk=pk)
        return Response(BookSerializer(book).data)

    def put(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookWriteSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            book = serializer.save()
            return Response(BookSerializer(book).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        book.is_active = False
        book.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InventoryUpdateView(APIView):
    """PATCH /api/books/<id>/inventory/ — adjust stock quantity."""

    def patch(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = InventoryUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        delta = serializer.validated_data["delta"]
        inv, _ = BookInventory.objects.get_or_create(book=book)
        new_qty = inv.stock_quantity + delta
        if new_qty < 0:
            return Response(
                {"error": "Insufficient stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        inv.stock_quantity = new_qty
        inv.save()
        return Response({"book_id": book.id, "stock_quantity": inv.stock_quantity})
