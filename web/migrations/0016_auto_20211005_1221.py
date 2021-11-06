# Generated by Django 3.2.7 on 2021-10-05 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0015_auto_20211002_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='migrated_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
