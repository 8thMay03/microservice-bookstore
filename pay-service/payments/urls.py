from django.urls import path
from .views import PaymentDetailView, PaymentByOrderView

urlpatterns = [
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("order/<int:order_id>/", PaymentByOrderView.as_view(), name="payment-by-order"),
]
