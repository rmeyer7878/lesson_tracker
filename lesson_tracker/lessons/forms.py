# # lessons/forms.py

# from django import forms
# from .models import Lesson, LessonPackage

# class TrackLessonForm(forms.ModelForm):
#     class Meta:
#         model = Lesson
#         fields = ['student', 'date', 'notes']

# class PurchaseLessonForm(forms.ModelForm):
#     class Meta:
#         model = LessonPackage  # Assuming you have a LessonPackage model
#         fields = ['student', 'package_name', 'lessons_purchased']
# lessons/forms.py

from django import forms
from .models import LessonPackage, Lesson, Student

class PurchaseLessonForm(forms.ModelForm):
    class Meta:
        model = LessonPackage
        fields = ['student', 'package_name', 'lessons_purchased']

class TrackLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['student', 'date', 'notes']
        
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'lessons_left']  # Fields to include in the form

    def clean_lessons_left(self):
        # Optional validation to ensure lessons_left is non-negative
        lessons_left = self.cleaned_data.get('lessons_left')
        if lessons_left < 0:
            raise forms.ValidationError("Lessons left cannot be negative.")
        return lessons_left
    
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['date', 'notes']