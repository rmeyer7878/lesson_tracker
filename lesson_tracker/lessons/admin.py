from django.contrib import admin
from .models import Student, LessonType, EmailTemplate, StudentLesson

# Register models with admin site

@admin.register(LessonType)
class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'duration', 'price', 'sale_price')  # Ensure all fields are valid

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
    
@admin.register(StudentLesson)
class StudentLessonAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson_type', 'quantity', 'scheduled', 'scheduled_datetime')
    list_filter = ('scheduled',)
    search_fields = ('student__user__username', 'lesson_type__name')  # Adjust based on your model relationships
