# lessons/admin.py

from django.contrib import admin
from .models import Student, LessonType, EmailTemplate

# Register models with admin site

@admin.register(LessonType)
class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price')

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject')
    
@admin.action(description='Mark selected students as inactive')
def mark_as_inactive(modeladmin, request, queryset):
    queryset.update(active=False)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'lessons_left')
    actions = [mark_as_inactive]
    

admin.site.unregister(LessonType)

class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'duration', 'price', 'sale_price')  # Ensure all fields are valid

admin.site.register(LessonType, LessonTypeAdmin)