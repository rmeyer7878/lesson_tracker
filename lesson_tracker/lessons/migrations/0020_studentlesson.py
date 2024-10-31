# Generated by Django 5.1.2 on 2024-10-30 22:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0019_remove_lessonpackage_student_remove_student_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('scheduled', models.BooleanField(default=False)),
                ('scheduled_datetime', models.DateTimeField(blank=True, null=True)),
                ('lesson_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lessons.lessontype')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]