from django.urls import path
from .views import RegisterView, LoginView, ProfileView, CustomerDetailView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="customer-register"),
    path("login/", LoginView.as_view(), name="customer-login"),
    path("profile/", ProfileView.as_view(), name="customer-profile"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="customer-detail"),
]
