from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from datetime import datetime
from .models import Flight, Order


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "confirm_password",
            "email",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "password": {"write-only": True},
            "confirm_password": {"write-only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Password fields don't match."}
            )

        try:
            validate_password(attrs["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "is_staff",
        ]


class FlightSerializer(serializers.ModelSerializer):
    origin_time = serializers.SerializerMethodField()
    destination_time = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        exclude = (
            "origin_dt",
            "destination_dt",
        )

    def get_origin_time(self, obj):
        return datetime.strftime(obj.origin_dt, "%d/%m/%Y %H:%M:%S")

    def get_destination_time(self, obj):
        return datetime.strftime(obj.destination_dt, "%d/%m/%Y %H:%M:%S")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
