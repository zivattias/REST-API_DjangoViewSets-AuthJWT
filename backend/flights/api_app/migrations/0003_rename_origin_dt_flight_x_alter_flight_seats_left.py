# Generated by Django 4.1.7 on 2023-02-28 16:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api_app", "0002_alter_order_table"),
    ]

    operations = [
        migrations.RenameField(
            model_name="flight",
            old_name="origin_dt",
            new_name="x",
        ),
        migrations.AlterField(
            model_name="flight",
            name="seats_left",
            field=models.IntegerField(db_column="seats_left"),
        ),
    ]
