from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


def home(request):
    return JsonResponse({"message": "Welcome to Project Nexus API"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    # user registration and auth
    path("api/users/", include("users.urls")),
    # product management
    path("api/products/", include("products.urls")),
    # orders
    path("api/orders/", include("orders.urls")),
    # cart
    path("api/cart/", include("carts.urls")),
    # cart
    path("api/payments/", include("payments.urls")),
    # jwt web token
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
