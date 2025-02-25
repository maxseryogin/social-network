# Generated by Django 5.1.6 on 2025-02-17 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0006_message_voice_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='voice_message',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='bio',
        ),
        migrations.AddField(
            model_name='profile',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_activity',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
