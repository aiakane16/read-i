# Generated by Django 5.1.2 on 2024-11-06 22:42

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0010_modules"),
    ]

    operations = [
        migrations.AddField(
            model_name="modules",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                default=1, editable=False, populate_from="title"
            ),
            preserve_default=False,
        ),
    ]
