from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Flight(models.Model):
    flight_num = models.CharField(
        db_column="flight_num", null=False, blank=False, max_length=24
    )
    origin_country = models.CharField(
        db_column="origin_country", null=False, blank=False, max_length=128
    )
    origin_city = models.CharField(
        db_column="origin_city", null=False, blank=False, max_length=128
    )
    origin_code = models.CharField(
        db_column="origin_code", null=False, blank=False, max_length=24
    )
    destination_country = models.CharField(
        db_column="destination_country", null=False, blank=False, max_length=128
    )
    destination_city = models.CharField(
        db_column="destination_city", null=False, blank=False, max_length=128
    )
    destination_code = models.CharField(
        db_column="destination_code", null=False, blank=False, max_length=24
    )
    origin_dt = models.DateTimeField(db_column="origin_dt", null=False, blank=False)
    destination_dt = models.DateTimeField(
        db_column="destination_dt", null=False, blank=False
    )
    total_seats = models.IntegerField(
        db_column="total_seats",
        null=False,
        blank=False,
        validators=[MinValueValidator(0)],
    )
    seats_left = models.IntegerField(db_column="seats_left")
    is_cancelled = models.BooleanField(db_column="is_cancelled", default=False)
    price = models.FloatField(db_column="price", null=False, blank=False)

    def __str__(self) -> str:
        return (
            f"Flight #{self.flight_num} ({self.origin_code} > {self.destination_code})"
        )

    def save(self, *args, **kwargs):
        # If seats_left is not given, defaults to total_seats
        if not self.seats_left:
            self.seats_left = self.total_seats
        super().save(*args, **kwargs)

    class Meta:
        db_table = "flights"


class Order(models.Model):
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, null=False, blank=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    seats = models.IntegerField(db_column="seats", null=False, blank=False)
    order_date = models.DateField(db_column="order_date", auto_now=True, null=True, blank=True)
    total_price = models.FloatField(db_column="total_price", null=True, blank=True)

    class Meta:
        db_table = "orders"

    def clean(self) -> ValidationError | None:
        if self.seats > self.flight.seats_left:
            raise ValidationError(
                {
                    "seats": "Number of ordered seats cannot exceed available seats of the flight."
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate the Order object with previously declared clean() method
        # Update order total_price according to Flight.price * self.seats
        self.total_price = self.seats * self.flight.price

        super().save(*args, **kwargs)  # Save the Order object in DB

        # Update the Flight object with the new seats_left value
        self.flight.seats_left -= self.seats
        self.flight.save(update_fields=["seats_left"])
