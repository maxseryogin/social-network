# Generated by Django 5.1.6 on 2025-03-04 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0010_notification'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
