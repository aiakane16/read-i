# Generated by Django 5.1.2 on 2024-10-27 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="students",
            name="updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="teachers",
            name="updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="users",
            name="updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
