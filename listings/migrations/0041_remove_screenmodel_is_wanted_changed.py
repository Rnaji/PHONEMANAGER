# Generated by Django 4.2.7 on 2024-02-21 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0040_screenmodel_is_wanted_changed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='screenmodel',
            name='is_wanted_changed',
        ),
    ]
