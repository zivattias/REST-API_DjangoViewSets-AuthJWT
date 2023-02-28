import os
import json
import django
import datetime

os.environ["DJANGO_SETTINGS_MODULE"] = "flights.settings"
django.setup()


from django.contrib.auth.models import User
from api_app.models import Flight, Order

# Apply is_staff=True to User.pk = 1 (Ziv Attias)
# user = User.objects.get(pk=1)
# user.is_staff = True
# user.save()

# DB population:
with open("backend/flights/api_app/MOCK_FLIGHT_DATA.json", "r") as data:
    flights = json.load(data)
    for flight in flights:
        Flight(
            flight_num=flight["flight_num"],
            origin_country=flight["origin_country"],
            origin_city=flight["origin_city"],
            origin_code=flight["origin_code"],
            destination_country=flight["destination_country"],
            destination_city=flight["destination_city"],
            destination_code=flight["destination_code"],
            origin_dt=datetime.datetime.fromtimestamp(int(flight["origin_dt"])),
            destination_dt=datetime.datetime.fromtimestamp(int(flight["destination_dt"])),
            total_seats=flight["total_seats"],
            seats_left=flight["seats_left"],
            is_cancelled=flight["is_cancelled"],
            price=flight["price"],
        ).save()

Order(flight=Flight.objects.get(pk=1), user=User.objects.get(pk=1), seats=2, order_date=datetime.datetime.now(), total_price=1000).save()
