from django.urls import path
from .views import BookListView, BookDetailView, InventoryUpdateView

urlpatterns = [
    path("", BookListView.as_view(), name="book-list"),
    path("<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    path("<int:pk>/inventory/", InventoryUpdateView.as_view(), name="book-inventory"),
]
