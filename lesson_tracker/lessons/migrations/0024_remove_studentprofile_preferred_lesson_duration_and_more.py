# Generated by Django 5.1.2 on 2024-10-31 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0023_remove_usercredits_lesson_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentprofile',
            name='preferred_lesson_duration',
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='day_of_week',
            field=models.CharField(choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday')], default='0', max_length=20),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='time',
            field=models.TimeField(default='09:00'),
        ),
    ]
