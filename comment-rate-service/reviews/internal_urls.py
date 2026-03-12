from django.urls import path
from .internal_views import InternalTopRatedBooksView

urlpatterns = [
    path("top-rated/", InternalTopRatedBooksView.as_view(), name="internal-top-rated"),
]
