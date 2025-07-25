from django.urls import path
from .views import RegisterUserView, LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
        path('register/', RegisterUserView.as_view(), name='user-registration'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
        ]
