# Generated by Django 3.1.4 on 2021-01-01 18:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20210101_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 1, 18, 2, 52, 158234)),
        ),
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
