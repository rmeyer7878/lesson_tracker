# Generated by Django 5.1.2 on 2024-10-29 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0013_alter_student_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessontype',
            name='duration',
            field=models.CharField(choices=[('0', '0 minutes'), ('20', '20 minutes'), ('30', '30 minutes'), ('45', '45 minutes'), ('60', '60 minutes')], max_length=20),
        ),
    ]