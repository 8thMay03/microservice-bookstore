from django.urls import path
from .internal_views import InternalCreateShipmentView

urlpatterns = [
    path("create/", InternalCreateShipmentView.as_view(), name="internal-create-shipment"),
]
