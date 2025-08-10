# urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartItemViewSet

router = DefaultRouter()
router.register(r"", CartViewSet, basename="cart")

# Manually define typed URLs for cart items
cart_item_list = CartItemViewSet.as_view({"get": "list", "post": "create"})
cart_item_detail = CartItemViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    path("", include(router.urls)),
    path("cart-items/", cart_item_list, name="cartitem-list"),
    path("cart-items/<int:pk>/", cart_item_detail, name="cartitem-detail"),
]