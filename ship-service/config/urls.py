from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/shipments/", include("shipments.urls")),
    path("internal/shipments/", include("shipments.internal_urls")),
]
