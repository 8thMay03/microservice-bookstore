from django.urls import path
from .views import CartView, CartItemView, CartItemDetailView, ClearCartView

urlpatterns = [
    path("<int:customer_id>/", CartView.as_view(), name="cart-detail"),
    path("<int:customer_id>/items/", CartItemView.as_view(), name="cart-item-add"),
    path("<int:customer_id>/items/<int:item_id>/", CartItemDetailView.as_view(), name="cart-item-detail"),
    path("<int:customer_id>/clear/", ClearCartView.as_view(), name="cart-clear"),
]
