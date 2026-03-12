from django.urls import path
from .views import ShipmentDetailView, ShipmentByOrderView, ShipmentStatusView, TrackShipmentView

urlpatterns = [
    path("<int:pk>/", ShipmentDetailView.as_view(), name="shipment-detail"),
    path("<int:pk>/status/", ShipmentStatusView.as_view(), name="shipment-status"),
    path("order/<int:order_id>/", ShipmentByOrderView.as_view(), name="shipment-by-order"),
    path("track/<uuid:tracking_number>/", TrackShipmentView.as_view(), name="shipment-track"),
]
