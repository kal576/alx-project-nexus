# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cartitem')

urlpatterns = [
    path('api/cart/', include(router.urls)),
]