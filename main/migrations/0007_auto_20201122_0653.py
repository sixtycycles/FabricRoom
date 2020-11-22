# Generated by Django 3.1.3 on 2020-11-22 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_slug', models.SlugField(max_length=200, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='note',
            name='subject',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='note',
            name='link',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='note_body',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='note',
            name='tags',
            field=models.ManyToManyField(to='main.Tag'),
        ),
    ]