# lessons/models.py
from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow null temporarily
    name = models.CharField(max_length=100)
    email = models.EmailField()
    lessons_left = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lessons')
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)  # Optional field to add notes for each lesson

    def __str__(self):
        return f"Lesson for {self.student.name} on {self.date}"

class LessonPackage(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # No need to import Student
    package_name = models.CharField(max_length=100)
    lessons_purchased = models.IntegerField()
    date_purchased = models.DateField(auto_now_add=True)
    lessons_used = models.IntegerField(default=0)

    def lessons_remaining(self):
        return self.lessons_purchased - self.lessons_used

    def __str__(self):
        return f"{self.package_name} ({self.lessons_purchased} lessons for {self.student.name})"

class LessonType(models.Model):
    name = models.CharField(max_length=100, default="Default Name")  # Ensure this has a default
    duration = models.CharField(max_length=20, choices=[
        ('20', '20 minutes'),
        ('30', '30 minutes'),
        ('45', '45 minutes'),
        ('60', '60 minutes'),
    ])
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sale_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    description = models.TextField(default="No description")  # Set a default value

    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price

    def display_price(self):
        return self.sale_price if self.is_on_sale() else self.price

    def __str__(self):
        return f"{self.name} - {self.get_duration_display()} (${self.display_price()})"

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return self.name
    
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add additional fields specific to students
    lessons_purchased = models.IntegerField(default=0)
    preferred_lesson_duration = models.CharField(
        max_length=20,
        choices=[('20', '20 minutes'), ('30', '30 minutes'), ('45', '45 minutes'), ('60', '60 minutes')],
        default='30'
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class StudentLesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)  # Track the number of lessons left for this type

    def __str__(self):
        return f"{self.student} - {self.lesson_type} ({self.quantity})"
