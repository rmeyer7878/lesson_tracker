# Generated by Django 5.1.2 on 2024-11-11 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0032_remove_studentprofile_added_credit_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='lesson_history',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]