from django import forms
from .models import LessonType, StudentProfile, User

class PurchaseLessonForm(forms.ModelForm):
    class Meta:
        model = LessonType
        fields = ['name', 'duration', 'price', 'sale_price', 'description']  # Include only valid fields

class StudentForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['lessons_purchased', 'lesson_duration', 'day_of_week', 'time']  # Update with actual fields in StudentProfile
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # or add 'first_name', 'last_name' as needed
