# from django.contrib import admin, messages
# from django import forms
# from django.shortcuts import render, redirect
# from django.urls import path
# from django.utils import timezone
# from .models import StudentProfile, LessonType
# import logging

# logger = logging.getLogger(__name__)

# class MarkLessonAttendedForm(forms.Form):
#     date = forms.DateField(widget=forms.SelectDateWidget, label="Select Lesson Date")

# @admin.register(LessonType)
# class LessonTypeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'duration', 'price', 'sale_price')

# @admin.register(StudentProfile)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = ('user', 'lessons_purchased', 'lesson_duration', 'day_of_week', 'time')
#     actions = ['mark_lesson_attended']

#     def mark_lesson_attended(self, request, queryset):
#         form = None
#         if 'apply' in request.POST:
#             form = MarkLessonAttendedForm(request.POST)
#             if form.is_valid():
#                 date = form.cleaned_data['date']
#                 count = 0
#                 for profile in queryset:
#                     if profile.lessons_purchased > 0:
#                         # Ensure lesson_history is a list; initialize if not
#                         if not isinstance(profile.lesson_history, list):
#                             profile.lesson_history = []
#                         # Append the selected date to lesson_history and decrement lessons_purchased
#                         profile.lesson_history.append({"date": date.isoformat()})
#                         profile.lessons_purchased -= 1
#                         profile.save()
#                         logger.debug(f"Updated lesson history for {profile.user.username} with date {date.isoformat()}")
#                         count += 1
#                     else:
#                         self.message_user(request, f"{profile.user.username} has no remaining lesson credits.", level=messages.WARNING)

#                 self.message_user(request, f"{count} lesson(s) marked as attended.", level=messages.SUCCESS)
#                 return redirect(request.get_full_path())
            
#         if not form:
#             form = MarkLessonAttendedForm(initial={'_selected_action': queryset.values_list('id', flat=True)})

#         return render(request, 'admin/mark_lesson_attended.html', {
#             'form': form,
#             'profiles': queryset,
#             'title': "Mark Lesson Attended",
#             'subtitle': "Please select a date for the lesson attendance",
#         })

#     mark_lesson_attended.short_description = "Mark Lesson Attended"

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('mark-lesson-attended/', self.admin_site.admin_view(self.mark_lesson_attended), name='mark_lesson_attended'),
#         ]
#         return custom_urls + urls
from django.contrib import admin, messages
from django import forms
from django.shortcuts import redirect, render
from .models import StudentProfile, LessonType
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@admin.register(LessonType)
class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'duration', 'price', 'sale_price')

class MarkLessonAttendedForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget, label="Select Lesson Date")

@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lessons_purchased', 'lesson_duration', 'day_of_week', 'time')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        profile = self.get_object(request, object_id)

        # Handle form submission
        if 'mark_lesson_attended' in request.POST:
            form = MarkLessonAttendedForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                
                # Update lesson history and decrement lessons_purchased
                if profile.lessons_purchased > 0:
                    if not isinstance(profile.lesson_history, list):
                        profile.lesson_history = []
                    profile.lesson_history.append({"date": date.isoformat()})
                    profile.lessons_purchased -= 1
                    profile.save()
                    
                    # Success message
                    self.message_user(request, "Lesson marked as attended.", level=messages.SUCCESS)
                    logger.info(f"Lesson marked attended for user {profile.user.username} on {date}")
                else:
                    # Warning if no credits are left
                    self.message_user(request, f"{profile.user.username} has no remaining lesson credits.", level=messages.WARNING)
                
                # Redirect back to the same page after processing form submission
                return redirect(request.path)

        else:
            form = MarkLessonAttendedForm()

        # Add custom context
        extra_context = extra_context or {}
        extra_context['mark_lesson_form'] = form

        # Ensure the base change_view response is always returned for display
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
