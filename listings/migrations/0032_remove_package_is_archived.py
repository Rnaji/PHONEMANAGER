# Generated by Django 4.2.7 on 2024-02-09 07:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0031_package_is_archived'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='is_archived',
        ),
    ]
