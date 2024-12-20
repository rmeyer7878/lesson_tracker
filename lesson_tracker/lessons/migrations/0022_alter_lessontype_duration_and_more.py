# Generated by Django 5.1.2 on 2024-10-31 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0021_delete_emailtemplate_delete_studentlesson'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessontype',
            name='duration',
            field=models.CharField(choices=[('20', '20 minutes'), ('30', '30 minutes'), ('45', '45 minutes'), ('60', '60 minutes'), ('0', '0 minutes')], max_length=20),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='lesson_duration',
            field=models.CharField(choices=[('20', '20 minutes'), ('30', '30 minutes'), ('45', '45 minutes'), ('60', '60 minutes'), ('0', '0 minutes')], default='30', max_length=20),
        ),
        migrations.DeleteModel(
            name='RecurringLesson',
        ),
    ]
