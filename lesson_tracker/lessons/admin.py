from django.contrib import admin
from .models import StudentProfile, LessonType, UserCredits, ScheduledLesson

# Register models with admin site

@admin.register(LessonType)
class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'duration', 'price', 'sale_price')

@admin.action(description='Mark selected students as inactive')
def mark_as_inactive(modeladmin, request, queryset):
    queryset.update(active=False)

@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lessons_purchased', 'preferred_lesson_duration')  # Adjusted to match StudentProfile fields
    def user_name(self, obj):
        return obj.user.username  # or obj.user.get_full_name() if you want the full name
    def user_email(self, obj):
        return obj.user.email
    user_name.short_description = 'Username'
    user_email.short_description = 'Email'
    #actions = [mark_as_inactive]

@admin.register(UserCredits)
class UserCreditsAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson_type', 'credits')
    search_fields = ('user__username', 'lesson_type__name')

@admin.register(ScheduledLesson)
class ScheduledLessonAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson_type', 'scheduled_time', 'is_cancelled')
    list_filter = ('is_cancelled',)
    search_fields = ('user__username', 'lesson_type__name')
