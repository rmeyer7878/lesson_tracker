
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile

User = get_user_model()

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    # Only save if the user has an associated Student profile
    if hasattr(instance, 'student'):
        instance.student.save()
