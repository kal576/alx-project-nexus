from django.urls import path, include
from .views import CartViewSet, CartItemViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')

urlpatterns = [
    path('', include(router.urls)),
]

