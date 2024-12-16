# Generated by Django 5.1.2 on 2024-10-31 14:17

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0006_sections_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sections",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                editable=False, populate_from="section"
            ),
        ),
    ]