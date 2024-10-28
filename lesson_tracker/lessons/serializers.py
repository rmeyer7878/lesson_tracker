# lessons/serializers.py

from rest_framework import serializers
from .models import Student, Lesson, LessonPackage

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class LessonPackageSerializer(serializers.ModelSerializer):
    lessons_remaining = serializers.IntegerField(source='lessons_remaining', read_only=True)

    class Meta:
        model = LessonPackage
        fields = '__all__'
