from rest_framework import viewsets
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

from .serializers import RegistrationSerializer, UserSerializer


# Registration serializer, available for anyone
class RegistrationAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


# Get self user data, available for authenticated User
class UserAPIView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.id)


# Get all users data or search by name, available for User.is_staff = True
class UsersAdminViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        if not name:
            return User.objects.all()

        if " " not in name:
            return User.objects.filter(
                Q(first_name__icontains=name) | Q(last_name__icontains=name)
            )

        first_name, last_name = name.split(" ")
        return User.objects.filter(
            Q(first_name__icontains=first_name) & Q(last_name__icontains=last_name)
        )
