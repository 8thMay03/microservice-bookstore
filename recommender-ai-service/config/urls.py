from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/recommendations/", include("recommender.urls")),
    path("internal/recommender/", include("recommender.internal_urls")),
]
