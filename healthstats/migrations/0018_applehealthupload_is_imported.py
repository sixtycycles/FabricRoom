# Generated by Django 3.2.2 on 2021-06-20 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthstats', '0017_applehealthupload_csv_data_dir'),
    ]

    operations = [
        migrations.AddField(
            model_name='applehealthupload',
            name='is_imported',
            field=models.BooleanField(default=False),
        ),
    ]
