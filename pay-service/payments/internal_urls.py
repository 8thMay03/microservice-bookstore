from django.urls import path
from .internal_views import InternalProcessPaymentView

urlpatterns = [
    path("process/", InternalProcessPaymentView.as_view(), name="internal-process-payment"),
]
