# Generated by Django 3.1.3 on 2020-11-22 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_profile_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(default='/srv/code/static/default_profile.jpg', upload_to='uploads/% Y/% m/% d/'),
        ),
    ]
