# Generated by Django 3.1.6 on 2021-03-18 04:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("healthstats", "0009_auto_20210317_0439"),
    ]

    operations = [
        migrations.CreateModel(
            name="StepData",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("creation_date", models.DateTimeField()),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                ("value", models.FloatField()),
                (
                    "author",
                    models.ForeignKey(
                        default=4,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
