# Generated by Django 5.1.2 on 2024-11-01 00:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0007_alter_sections_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="students",
            name="section",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="section_class_list",
                to="apps.sections",
            ),
        ),
    ]
