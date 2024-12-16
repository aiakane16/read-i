# Generated by Django 5.1.2 on 2024-12-09 08:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apps", "0025_alter_answer_question"),
    ]

    operations = [
        migrations.AlterField(
            model_name="answer",
            name="question",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="answer",
                to="apps.question",
            ),
        ),
    ]
