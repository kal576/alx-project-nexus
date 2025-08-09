from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

router = DeafultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = router.urls
