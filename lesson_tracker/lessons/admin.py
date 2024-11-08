# # from django.contrib import admin, messages
# # from django import forms
# # from django.shortcuts import render, redirect
# # from django.urls import path
# # from django.utils import timezone
# # from .models import StudentProfile, LessonType
# # import logging

# # logger = logging.getLogger(__name__)

# # class MarkLessonAttendedForm(forms.Form):
# #     date = forms.DateField(widget=forms.SelectDateWidget, label="Select Lesson Date")

# # @admin.register(LessonType)
# # class LessonTypeAdmin(admin.ModelAdmin):
# #     list_display = ('name', 'description', 'duration', 'price', 'sale_price')

# # @admin.register(StudentProfile)
# # class StudentAdmin(admin.ModelAdmin):
# #     list_display = ('user', 'lessons_purchased', 'lesson_duration', 'day_of_week', 'time')
# #     actions = ['mark_lesson_attended']

# #     def mark_lesson_attended(self, request, queryset):
# #         form = None
# #         if 'apply' in request.POST:
# #             form = MarkLessonAttendedForm(request.POST)
# #             if form.is_valid():
# #                 date = form.cleaned_data['date']
# #                 count = 0
# #                 for profile in queryset:
# #                     if profile.lessons_purchased > 0:
# #                         # Ensure lesson_history is a list; initialize if not
# #                         if not isinstance(profile.lesson_history, list):
# #                             profile.lesson_history = []
# #                         # Append the selected date to lesson_history and decrement lessons_purchased
# #                         profile.lesson_history.append({"date": date.isoformat()})
# #                         profile.lessons_purchased -= 1
# #                         profile.save()
# #                         logger.debug(f"Updated lesson history for {profile.user.username} with date {date.isoformat()}")
# #                         count += 1
# #                     else:
# #                         self.message_user(request, f"{profile.user.username} has no remaining lesson credits.", level=messages.WARNING)

# #                 self.message_user(request, f"{count} lesson(s) marked as attended.", level=messages.SUCCESS)
# #                 return redirect(request.get_full_path())
            
# #         if not form:
# #             form = MarkLessonAttendedForm(initial={'_selected_action': queryset.values_list('id', flat=True)})

# #         return render(request, 'admin/mark_lesson_attended.html', {
# #             'form': form,
# #             'profiles': queryset,
# #             'title': "Mark Lesson Attended",
# #             'subtitle': "Please select a date for the lesson attendance",
# #         })

# #     mark_lesson_attended.short_description = "Mark Lesson Attended"

# #     def get_urls(self):
# #         urls = super().get_urls()
# #         custom_urls = [
# #             path('mark-lesson-attended/', self.admin_site.admin_view(self.mark_lesson_attended), name='mark_lesson_attended'),
# #         ]
# #         return custom_urls + urls
from django.contrib import admin, messages
from django import forms
from django.shortcuts import redirect, render
from .models import StudentProfile, LessonType
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
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
                    if profile.lessons_purchased == 1:
                        subject = "One Lesson Left"
                        message = (
                            f"Dear {profile.user.username},\n\n"
                            f"You have one lesson left in your account.\n"
                            "We look forward to helping you achieve your vocal goals.\n\n"
                            "Best regards,\n"
                            "Candice Meyer Vocal Studio"
                        )
                        recipient_email = profile.user.email
                        from_email = settings.DEFAULT_FROM_EMAIL

                        # Send the email
                        send_mail(
                            subject,
                            message,
                            from_email,
                            [recipient_email],
                            fail_silently=False,
                        )
                    if profile.lessons_purchased == 0:
                        subject = "No Lessons Left"
                        message = (
                            f"Dear {profile.user.username},\n\n"
                            f"You have no lessons left in your account.\n"
                            "We look forward to helping you achieve your vocal goals.\n\n"
                            "Best regards,\n"
                            "Candice Meyer Vocal Studio"
                        )
                        recipient_email = profile.user.email
                        from_email = settings.DEFAULT_FROM_EMAIL

                        # Send the email
                        send_mail(
                            subject,
                            message,
                            from_email,
                            [recipient_email],
                            fail_silently=False,
                        )        
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


# from django.contrib import admin, messages
# from django.core.mail import send_mail
# from django import forms
# from django.utils.html import format_html
# from django.conf import settings
# from .models import StudentProfile, LessonType



# @admin.register(LessonType)
# class LessonTypeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'duration', 'price', 'sale_price')

# class MarkLessonAttendedForm(forms.Form):
#     date = forms.DateField(widget=forms.SelectDateWidget, label="Select Lesson Date")

# # Define forms for customizing email content
# class EmailContentForm(forms.Form):
#     low_credit_email = forms.CharField(widget=forms.Textarea, label="Low Credit Email Content", required=False)
#     no_credit_email = forms.CharField(widget=forms.Textarea, label="No Credit Email Content", required=False)

# @admin.register(StudentProfile)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = ('user', 'lessons_purchased', 'lesson_duration', 'day_of_week', 'time')
#     readonly_fields = ('email_preview',)

#     # Custom change form for additional email customization fields
#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         profile = self.get_object(request, object_id)

#         # Load or initialize email content form
#         email_content_form = EmailContentForm(initial={
#             'low_credit_email': profile.low_credit_email if hasattr(profile, 'low_credit_email') else "You have only 1 lesson credit left. Please purchase more.",
#             'no_credit_email': profile.no_credit_email if hasattr(profile, 'no_credit_email') else "You have no lesson credits left. Please purchase more."
#         })

#         # Handle form submission
#         if request.method == "POST":
#             email_content_form = EmailContentForm(request.POST)
#             if email_content_form.is_valid():
#                 # Update profile with customized email content
#                 profile.low_credit_email = email_content_form.cleaned_data['low_credit_email']
#                 profile.no_credit_email = email_content_form.cleaned_data['no_credit_email']
#                 profile.save()
#                 messages.success(request, "Email content updated successfully.")

#         # Add the email content form and preview to extra context
#         extra_context = extra_context or {}
#         extra_context['email_content_form'] = email_content_form
#         extra_context['email_preview'] = self.email_preview(profile)

#         return super().change_view(request, object_id, form_url, extra_context=extra_context)

#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
        
#         # Check lesson credits and send email if they reach 1 or 0
#         if obj.lessons_purchased == 1:
#             self.send_custom_email(obj.user.email, "Low Credit Alert", obj.low_credit_email)
#             messages.info(request, f"Low credit email sent to {obj.user.email}.")
#         elif obj.lessons_purchased == 0:
#             self.send_custom_email(obj.user.email, "No Credit Alert", obj.no_credit_email)
#             messages.info(request, f"No credit email sent to {obj.user.email}.")

#     def send_custom_email(self, recipient, subject, message):
#         send_mail(
#             subject,
#             message,
#             settings.DEFAULT_FROM_EMAIL,
#             [recipient],
#             fail_silently=False,
#         )

#     def email_preview(self, profile):
#         """HTML preview for the customized email content"""
#         return format_html(
#             "<b>Low Credit Email:</b><br>{}<br><br><b>No Credit Email:</b><br>{}",
#             profile.low_credit_email if hasattr(profile, 'low_credit_email') else "You have only 1 lesson credit left. Please purchase more.",
#             profile.no_credit_email if hasattr(profile, 'no_credit_email') else "You have no lesson credits left. Please purchase more."
#         )

#     email_preview.short_description = "Email Preview"
