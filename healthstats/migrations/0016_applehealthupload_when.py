# Generated by Django 3.2.2 on 2021-06-19 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthstats', '0015_applehealthupload_is_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='applehealthupload',
            name='when',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
