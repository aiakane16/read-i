# Generated by Django 5.1.2 on 2024-10-31 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0004_alter_students_options_alter_users_options_sections"),
    ]

    operations = [
        migrations.AddField(
            model_name="students",
            name="address",
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="students",
            name="birthday",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="users",
            name="middle_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="users",
            name="first_name",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="users",
            name="last_name",
            field=models.CharField(max_length=255),
        ),
    ]
