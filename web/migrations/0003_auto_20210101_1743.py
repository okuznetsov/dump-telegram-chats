# Generated by Django 3.1.4 on 2021-01-01 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20210101_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='chat',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='web.chat'),
        ),
        migrations.AddField(
            model_name='message',
            name='text',
            field=models.TextField(blank=True, default=None),
        ),
        migrations.AddField(
            model_name='message',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='web.user'),
        ),
    ]
