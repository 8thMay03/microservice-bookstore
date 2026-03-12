from django.urls import path
from .internal_views import InternalOrderHistoryView

urlpatterns = [
    path("customer/<int:customer_id>/history/", InternalOrderHistoryView.as_view(), name="internal-order-history"),
]
