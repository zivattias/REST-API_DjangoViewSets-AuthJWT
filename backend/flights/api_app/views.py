from rest_framework import serializers
from datetime import datetime
from rest_framework import viewsets
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Flight, Order
from .utils import parse_datetime_str, validate_datetime
from .serializers import (
    RegistrationSerializer,
    UserSerializer,
    FlightSerializer,
    OrderSerializer,
)


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

        names = name.split(" ")
        if len(names) > 1:
            first_name = names[0]
            last_name = names[1]
            return User.objects.filter(
                first_name__icontains=first_name, last_name__icontains=last_name
            )

        return User.objects.filter(
            Q(first_name__icontains=names[0]) | Q(last_name__icontains=names[0])
        )


# Get all flights / by flight_num & search for a specific flight by origin, destination, origin_date and destination_date range, price range, is_cancelled
class FlightsViewSet(viewsets.ModelViewSet):
    serializer_class = FlightSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        data_copy = request.data.copy()
        data_copy["origin_dt"] = validate_datetime(data_copy.get("origin_dt"))
        data_copy["destination_dt"] = validate_datetime(
            data_copy.get("destination_dt")
        )

        serializer = self.get_serializer(data=data_copy)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        data_copy = request.data.copy()
        if "origin_dt" in data_copy:
            data_copy["origin_dt"] = validate_datetime(data_copy.get("origin_dt"))
        if "destination_dt" in data_copy:
            data_copy["destination_dt"] = validate_datetime(
                data_copy.get("destination_dt")
            )

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data_copy, partial=True)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = Flight.objects.all()
        # Convert query params to a dict() for better data accessibility code-wise
        params = self.request.query_params.dict()
        # Start filtering the QuerySet according to query params
        if params.get("origin_city") is not None:
            qs = qs.filter(origin_city__iexact=params["origin_city"])
        if params.get("destination_city") is not None:
            qs = qs.filter(destination_city__iexact=params["destination_city"])
        if params.get("min_price") is not None:
            qs = qs.filter(price__gte=params["min_price"])
        if params.get("max_price") is not None:
            qs = qs.filter(price__lte=params["max_price"])
        if params.get("is_cancelled") is not None:
            is_cancelled = params["is_cancelled"].lower() == "true"
            qs = qs.filter(is_cancelled=is_cancelled)

        # For origin date & destination date here are 2 acceptable formats for query params:
        # 1. DD/MM/YYYY
        # 2. DD/MM/YYYY HH:MM
        # Hence, the 'if " " in date' check @ parse_datetime_str()!

        if params.get("origin_date") is not None:
            origin_datetime = parse_datetime_str(params["origin_date"])
            if origin_datetime is None:
                return qs.none()
            qs = qs.filter(origin_dt__gte=origin_datetime)

        if params.get("destination_date") is not None:
            dest_datetime = parse_datetime_str(params["destination_date"])
            if dest_datetime is None:
                return qs.none()
            qs = qs.filter(destination_dt__lte=dest_datetime)

        return qs


# Order serializer, staff: create, update, get all orders, search by flight_num & name (first_name & last_name) | authenticated: get their own order
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if not request.user.is_staff:
            if request.user.id != order.user.id:
                return Response(
                    {"order_id": "The order is owned by a different user."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        serializer = self.get_serializer(order, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            return Order.objects.filter(user=user.id)
        else:
            qs = Order.objects.all()
            params = self.request.query_params.dict()
            if params.get("flight_id") is not None:
                qs = qs.filter(flight=params["flight_id"])
            if params.get("flight_num") is not None:
                qs = qs.filter(flight__flight_num=params["flight_num"])
            if params.get("name") is not None:
                if " " in params["name"]:
                    names = params["name"].split(" ")
                    first_name = names[0]
                    last_name = names[1]
                    qs = qs.filter(
                        Q(user__first_name__icontains=first_name)
                        & Q(user__last_name__icontains=last_name)
                    )
                else:
                    qs = qs.filter(
                        Q(user__first_name__icontains=params["name"])
                        | Q(user__last_name__icontains=params["name"])
                    )
            return qs
