# lessons/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from .models import Student

@shared_task
def send_reminder_emails():
    students = Student.objects.filter(lessons_left__lte=3)
    for student in students:
        send_mail(
            'Reminder: Low Lesson Count',
            f'Dear {student.name}, you have {student.lessons_left} lessons left. Please consider purchasing more lessons.',
            'from@example.com',
            [student.email],
            fail_silently=False,
        )
