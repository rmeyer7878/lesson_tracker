from django.db import models
from django.contrib.auth.models import User

def get_default_user():
    try:
        return User.objects.get(username='defaultuser').id
    except User.DoesNotExist:
        return None

# Tracks lessons left by the student, related to each lesson type
class UserCredits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credits')
    lesson_type = models.ForeignKey('LessonType', on_delete=models.CASCADE)
    credits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.credits} credits for {self.lesson_type.name}"

# LessonType represents different types of lessons available for purchase
class LessonType(models.Model):
    name = models.CharField(max_length=100, default="Default Name")
    duration = models.CharField(max_length=20, choices=[
        ('20', '20 minutes'),
        ('30', '30 minutes'),
        ('45', '45 minutes'),
        ('60', '60 minutes'),
    ])
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sale_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    description = models.TextField(default="No description")

    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price

    def display_price(self):
        return self.sale_price if self.is_on_sale() else self.price

    def __str__(self):
        return f"{self.name} - {self.get_duration_display()} (${self.display_price()})"

# ScheduledLesson represents individual lessons scheduled by the superuser
class ScheduledLesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scheduled_lessons")
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    is_cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"Scheduled {self.lesson_type.name} for {self.user.username} on {self.scheduled_time}"

# Profile extension to store additional student information
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    lessons_purchased = models.IntegerField(default=0)
    preferred_lesson_duration = models.CharField(
        max_length=20,
        choices=[('20', '20 minutes'), ('30', '30 minutes'), ('45', '45 minutes'), ('60', '60 minutes')],
        default='30'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

