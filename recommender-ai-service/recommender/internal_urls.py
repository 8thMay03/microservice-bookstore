from django.urls import path
from .internal_views import InternalBehaviorEventsView

urlpatterns = [
    path("behavior-events/", InternalBehaviorEventsView.as_view(), name="internal-behavior-events"),
]
