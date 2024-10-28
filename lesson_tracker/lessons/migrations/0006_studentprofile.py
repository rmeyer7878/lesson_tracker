# Generated by Django 5.1.2 on 2024-10-27 20:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0005_remove_lessontype_name_lessontype_duration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lessons_purchased', models.IntegerField(default=0)),
                ('preferred_lesson_duration', models.CharField(choices=[('20', '20 minutes'), ('30', '30 minutes'), ('45', '45 minutes'), ('60', '60 minutes')], default='30', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
