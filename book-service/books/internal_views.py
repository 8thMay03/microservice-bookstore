from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Book
from .serializers import BookSerializer


class InternalBookDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        book = get_object_or_404(Book.objects.select_related("inventory"), pk=pk)
        return Response(BookSerializer(book).data)


class InternalBulkDetailView(APIView):
    """POST /internal/books/bulk/ — fetch multiple books by IDs."""
    permission_classes = [AllowAny]

    def post(self, request):
        ids = request.data.get("ids", [])
        books = Book.objects.select_related("inventory").filter(id__in=ids)
        return Response(BookSerializer(books, many=True).data)
