# Generated by Django 5.0 on 2024-01-06 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0028_package_total_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brokenscreen',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='package',
            name='reference',
            field=models.CharField(max_length=40, unique=True),
        ),
    ]
