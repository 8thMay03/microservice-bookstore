from django.urls import path
from .internal_views import InternalBookDetailView, InternalBulkDetailView

urlpatterns = [
    path("<int:pk>/", InternalBookDetailView.as_view(), name="internal-book-detail"),
    path("bulk/", InternalBulkDetailView.as_view(), name="internal-book-bulk"),
]
