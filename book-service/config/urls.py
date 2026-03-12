from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/books/", include("books.urls")),
    path("internal/books/", include("books.internal_urls")),
]
