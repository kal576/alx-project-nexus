from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, order_now

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
        path('orders/now/', order_now, name='order-now'),
        ]

urlpatterns += router.urls
