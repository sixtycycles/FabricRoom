# Generated by Django 3.1.6 on 2021-02-13 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0003_remove_note_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="tags",
            field=models.ManyToManyField(blank=True, to="blog.Tag"),
        ),
    ]
