from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserAPIView, RegistrationAPIView, UsersAdminViewSet

urlpatterns = [
    path("users/", UsersAdminViewSet.as_view({"get": "list"}), name="admin_users"),
    path("auth/self/", UserAPIView.as_view({"get": "retrieve"}), name="self_data"),
    path("auth/signup/", RegistrationAPIView.as_view(), name="signup"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
