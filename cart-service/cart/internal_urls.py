from django.urls import path
from .internal_views import InternalCreateCartView, InternalCartDetailView

urlpatterns = [
    path("create/", InternalCreateCartView.as_view(), name="internal-cart-create"),
    path("<int:customer_id>/", InternalCartDetailView.as_view(), name="internal-cart-detail"),
]
