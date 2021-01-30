# Generated by Django 3.1.3 on 2020-12-24 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthstats', '0002_auto_20201224_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='symptom',
            name='slug',
            field=models.SlugField(default='slugger-slug', verbose_name='symptoms'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='symptom',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]