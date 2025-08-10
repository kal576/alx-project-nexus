from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductsViewSet, InventoryViewSet

router = DefaultRouter()
router.register(r"", ProductsViewSet)
router.register(r"inventory", InventoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
