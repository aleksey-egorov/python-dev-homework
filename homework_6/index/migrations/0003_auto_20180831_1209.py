# Generated by Django 2.1 on 2018-08-31 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_auto_20180831_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='answers',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='votes',
            field=models.IntegerField(default=0),
        ),
    ]
