# Generated by Django 5.0.4 on 2024-04-28 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_orderitem_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="ordered_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
