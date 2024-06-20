# Generated by Django 5.0.4 on 2024-04-30 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_alter_item_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="category",
            field=models.CharField(
                choices=[
                    ("shirt", "shirt"),
                    ("shorts", "shorts"),
                    ("outwear", "outwear"),
                    ("shoes", "shoes"),
                    ("bats", "bats"),
                    ("T-shirts", "T-shirts"),
                    ("bags", "bags"),
                    ("pants", "pants"),
                    ("accessories", "accessories"),
                ],
                default=True,
                max_length=64,
            ),
        ),
    ]
