# Generated by Django 5.0.2 on 2024-02-12 20:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthstats', '0018_applehealthupload_is_imported'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BloodPressure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_date', models.DateTimeField(auto_now_add=True)),
                ('systolic_pressure', models.PositiveIntegerField(default=0)),
                ('diastolic_pressure', models.PositiveIntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
