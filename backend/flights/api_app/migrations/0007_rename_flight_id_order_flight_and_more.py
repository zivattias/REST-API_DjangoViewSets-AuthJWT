# Generated by Django 4.1.7 on 2023-03-01 07:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api_app", "0006_rename_flight_order_flight_id_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="flight_id",
            new_name="flight",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="user_id",
            new_name="user",
        ),
    ]
