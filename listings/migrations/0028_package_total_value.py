# Generated by Django 5.0 on 2024-01-04 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0027_remove_brokenscreen_package_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='total_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
