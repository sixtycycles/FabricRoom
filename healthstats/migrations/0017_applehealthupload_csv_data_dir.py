# Generated by Django 3.2.2 on 2021-06-19 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthstats', '0016_applehealthupload_when'),
    ]

    operations = [
        migrations.AddField(
            model_name='applehealthupload',
            name='csv_data_dir',
            field=models.CharField(default='/srv/code/media/processed/generic', max_length=500),
            preserve_default=False,
        ),
    ]