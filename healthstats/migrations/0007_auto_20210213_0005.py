# Generated by Django 3.1.6 on 2021-02-13 00:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("healthstats", "0006_auto_20210116_2140"),
    ]

    operations = [
        migrations.RenameField(
            model_name="symptom",
            old_name="name",
            new_name="slug",
        ),
    ]
