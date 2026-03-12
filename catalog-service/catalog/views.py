from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category
from .serializers import CategorySerializer, CategoryWriteSerializer
from .auth import ManagerJWTAuthentication
from .permissions import IsManagerOrReadOnly


class CategoryListView(APIView):
    authentication_classes = [ManagerJWTAuthentication]
    permission_classes = [IsManagerOrReadOnly]
    """GET /api/catalog/categories/ — list root categories with children."""

    def get(self, request):
        categories = Category.objects.filter(parent=None).prefetch_related("children")
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        serializer = CategoryWriteSerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    """GET/PUT/DELETE /api/catalog/categories/<id>/"""
    authentication_classes = [ManagerJWTAuthentication]
    permission_classes = [IsManagerOrReadOnly]

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        return Response(CategorySerializer(category).data)

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategoryWriteSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CategorySerializer(category).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
