# Generated by Django 4.2.7 on 2024-02-08 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0029_alter_brokenscreen_id_alter_package_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='brokenscreen',
            name='diag_question_1',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokenscreen',
            name='diag_question_2',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokenscreen',
            name='diag_question_3',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokenscreen',
            name='diag_question_4',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokenscreen',
            name='diag_question_5',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokenscreen',
            name='diag_question_6',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokenscreen',
            name='diag_question_7',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokenscreen',
            name='diag_question_8',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brokenscreen',
            name='diag_question_9',
            field=models.TextField(blank=True, null=True),
        ),
    ]
