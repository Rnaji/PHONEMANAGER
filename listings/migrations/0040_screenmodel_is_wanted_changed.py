# Generated by Django 4.2.7 on 2024-02-21 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0039_brokenscreen_diag_question_10_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='screenmodel',
            name='is_wanted_changed',
            field=models.BooleanField(default=False),
        ),
    ]
