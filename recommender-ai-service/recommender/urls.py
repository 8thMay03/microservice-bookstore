from django.urls import path
from .views import RecommendationView

urlpatterns = [
    path("<int:customer_id>/", RecommendationView.as_view(), name="recommendations"),
]
