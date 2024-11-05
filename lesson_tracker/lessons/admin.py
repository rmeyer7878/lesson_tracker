from django.contrib import admin
from .models import StudentProfile, LessonType

# Register models with admin site

@admin.register(LessonType)
class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'duration', 'price', 'sale_price')

@admin.action(description='Mark selected students as inactive')
def mark_as_inactive(modeladmin, request, queryset):
    queryset.update(active=False)

@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lessons_purchased', 'lesson_duration', 'day_of_week', 'time')  # Adjusted to match StudentProfile fields
    def user_name(self, obj):
        return obj.user.username  # or obj.user.get_full_name() if you want the full name
    def user_email(self, obj):
        return obj.user.email
    user_name.short_description = 'Username'
    user_email.short_description = 'Email'
    #actions = [mark_as_inactive]

