# Generated by Django 3.1.6 on 2021-03-08 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthstats', '0007_auto_20210213_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthevent',
            name='feels_rating',
            field=models.IntegerField(blank=True, help_text='How bad do you feel? Enter a number between 0 and 10, where 10 is bad, 0 is good', null=True),
        ),
    ]
