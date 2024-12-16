# Generated by Django 5.1.2 on 2024-12-08 14:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0018_user_module_answer"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserExperience",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_points", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="experience",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]