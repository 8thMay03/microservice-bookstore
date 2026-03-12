from django.urls import path, re_path
from proxy.views import GatewayProxyView, HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    # All /api/<service>/... traffic is forwarded to the matching downstream service.
    re_path(r"^api/(?P<service>[^/]+)/(?P<path>.*)$", GatewayProxyView.as_view(), name="proxy"),
]
