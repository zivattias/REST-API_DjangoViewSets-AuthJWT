from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserAPIView,
    RegistrationAPIView,
    UsersAdminViewSet,
    FlightsViewSet,
    OrderViewSet,
    BlacklistRefreshToken
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"flights", FlightsViewSet, basename="flights")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("users/", UsersAdminViewSet.as_view({"get": "list"}), name="admin_users"),
    path("auth/self/", UserAPIView.as_view({"get": "retrieve"}), name="self_data"),
    path("auth/signup/", RegistrationAPIView.as_view(), name="signup"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", BlacklistRefreshToken.as_view(), name="token_blacklist")
]

urlpatterns.extend(router.urls)
