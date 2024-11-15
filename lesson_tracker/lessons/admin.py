from django.contrib import admin, messages
from django import forms
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from .models import StudentProfile, LessonType
from .views import shared_calendar_view
import logging

logger = logging.getLogger(__name__)


# Register LessonType Admin
@admin.register(LessonType)
class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'duration', 'price', 'sale_price')


# Form for marking lessons attended
class MarkLessonAttendedForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget, label="Select Lesson Date")


# Student Profile Admin
@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lessons_purchased', 'lesson_duration', 'day_of_week', 'time', 'view_calendar_link')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        profile = self.get_object(request, object_id)

        # Handle form submission for marking lessons attended
        if 'mark_lesson_attended' in request.POST:
            form = MarkLessonAttendedForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                if profile.lessons_purchased > 0:
                    if not isinstance(profile.lesson_history, list):
                        profile.lesson_history = []

                    profile.lesson_history.append({"date": date.isoformat()})
                    profile.lessons_purchased -= 1
                    profile.save()

                    # Send email notifications based on lessons left
                    if profile.lessons_purchased == 1:
                        self.send_email(profile, "One Lesson Left", "You have one lesson left.")
                    elif profile.lessons_purchased == 0:
                        self.send_email(profile, "No Lessons Left", "You have no lessons left.")

                    self.message_user(request, "Lesson marked as attended.", level=messages.SUCCESS)
                else:
                    self.message_user(request, "No remaining lesson credits.", level=messages.WARNING)

                return redirect(request.path)
        else:
            form = MarkLessonAttendedForm()

        extra_context = extra_context or {}
        extra_context['mark_lesson_form'] = form

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def view_calendar_link(self, obj):
        url = reverse('shared_calendar')
        return format_html('<a href="{}" target="_blank">View Calendar</a>', url)

    view_calendar_link.short_description = 'Shared Calendar'

    # Helper method to send email
    def send_email(self, profile, subject, message_body):
        subject = f"{subject} - Candice Meyer Vocal Studio"
        message = (
            f"Dear {profile.user.username},\n\n"
            f"{message_body}\n"
            "We look forward to helping you achieve your vocal goals.\n\n"
            "Best regards,\n"
            "Candice Meyer Vocal Studio"
        )
        recipient_email = profile.user.email
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(subject, message, from_email, [recipient_email], fail_silently=False)


# URL Configuration for Shared Calendar
from django.urls import path

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('calendar/', self.admin_view(shared_calendar_view), name='shared_calendar'),
        ]
        return custom_urls + urls

# Use the custom admin site if desired
admin_site = CustomAdminSite(name='custom_admin')
