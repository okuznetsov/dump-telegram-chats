# Generated by Django 3.1.4 on 2021-01-01 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_auto_20210101_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='disabled',
            field=models.NullBooleanField(default=False),
        ),
    ]