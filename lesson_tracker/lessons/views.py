# lessons/views.py

import stripe
from django.shortcuts import render, get_object_or_404, redirect
from .models import StudentProfile, LessonType
from .forms import PurchaseLessonForm, StudentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect
import logging
from django.core.mail import send_mail
from django.conf import settings
stripe.api_key = settings.SECRET_KEY

logger = logging.getLogger('myapp')  # Replace 'myapp' with the name you set in LOGGING configuration

# Home and About Views
def home(request):
    return render(request, 'lessons/home.html')

def about(request):
    return render(request, 'lessons/about.html')

# Student Views
@login_required
def student_list(request):
    if not request.user.is_superuser:
        return redirect('home')
    #students = Student.objects.all()
    students = StudentProfile.objects.filter(user=request.user)
    return render(request, 'lessons/student_list.html', {'students': students})

def student_detail(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    return render(request, 'lessons/student_detail.html', {'student': student})

def student_delete(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('students')
    return render(request, 'lessons/student_confirm_delete.html', {'student': student})

def student_lessons(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    lessons = student.studentlesson_set.all()  # Retrieves all StudentLesson records related to the student

    if request.method == 'POST':
        form = PurchaseLessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.student = student
            lesson.save()
            return redirect('student_lessons', pk=student.pk)
    else:
        form = PurchaseLessonForm()

    return render(request, 'lessons/student_lessons.html', {
        'student': student,
        'lessons': lessons,
        'form': form,
    })

@login_required
def profile(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    lessons_purchased = student_profile.lessons_purchased  # Total lessons purchased

    return render(request, 'lessons/profile.html', {
        'lessons_purchased': lessons_purchased,
        'student_profile': student_profile
    })


def cart_view(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # Update the cart count in the session based on the current cart contents
    request.session['cart_count'] = sum(item['quantity'] for item in cart.values())
    request.session.modified = True  # Ensure session data is saved

    return render(request, 'lessons/cart.html', {'cart': cart, 'total': total})


@login_required
def add_to_cart(request, lesson_id):
    lesson = get_object_or_404(LessonType, id=lesson_id)
    
    # Get the cart from the session or initialize it as an empty dictionary
    cart = request.session.get('cart', {})

    lesson_id_str = str(lesson_id)  # Ensure lesson_id is treated as a string in session data
    if lesson_id_str in cart:
        # If lesson is already in the cart, increment the quantity
        cart[lesson_id_str]['quantity'] += 1
    else:
        # Add a new entry if the lesson is not in the cart
        cart[lesson_id_str] = {
            'name': lesson.name,
            'price': float(lesson.display_price()),  # Use display_price if you have sales prices
            'quantity': 1,
        }

    # Update the session cart
    request.session['cart'] = cart

    # Update the cart count in the session
    request.session['cart_count'] = sum(item['quantity'] for item in cart.values())

    # Mark the session as modified to ensure it’s saved
    request.session.modified = True

    return redirect('store')

# @login_required
# @transaction.atomic  # Ensures all changes are saved together or not at all
# def checkout_view(request):
#     logger.info("Checkout view accessed")
#     cart = request.session.get('cart', {})
#     total_lessons = sum(item['quantity'] for item in cart.values())
#     total_amount = int(sum(item['price'] * item['quantity'] for item in cart.values()) * 100)  # Convert to cents

#     # If there are no items in the cart, redirect with a message
#     if total_lessons == 0 or total_amount == 0:
#         messages.info(request, "Your cart is empty or has invalid items.")
#         return redirect('cart')

#     # Check if the user has a profile and update lesson credits
#     try:
#         profile = request.user.student_profile
#         profile.lessons_purchased += total_lessons
#         profile.save()

#         # Clear the cart after saving profile information
#         request.session['cart'] = {}
#         request.session['cart_count'] = 0

#         # Create the Stripe PaymentIntent
#         payment_intent = stripe.PaymentIntent.create(
#             amount=total_amount,
#             currency='usd',
#             payment_method_types=['card'],
#         )
#         request.session['payment_intent_id'] = payment_intent['id']
#         logger.info(f"PaymentIntent created: {payment_intent['id']}")

#         # Render checkout page with Stripe payment details
#         return render(request, 'checkout.html', {
#             'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
#             'client_secret': payment_intent['client_secret']
#         })
#     except stripe.error.StripeError as e:
#         logger.error(f"Stripe error during PaymentIntent creation: {e.user_message}")
#         return redirect('cart')
#     except StudentProfile.DoesNotExist:
#         logger.error("Student profile not found for user.")
#         return redirect('cart')
#     except Exception as e:
#         logger.error(f"Unexpected error during checkout: {e}")
#         return redirect('cart')


# @login_required
# def checkout_view(request):
#     cart = request.session.get('cart', {})
#     total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
    
#     # Create a PaymentIntent regardless of the request method to ensure `client_secret` is available
#     intent = stripe.PaymentIntent.create(
#         amount=int(total_amount * 100),  # Stripe expects the amount in cents
#         currency="usd",
#     )
    
#     if request.method == 'POST':
#         try:
#             # Process Stripe payment (already created intent)
#             stripe.PaymentIntent.confirm(
#                 intent.id,
#                 payment_method=request.POST['payment_method_id']
#             )

#             # Update lessons_purchased field in StudentProfile
#             for lesson_id, item in cart.items():
#                 quantity = item['quantity']
#                 lessons_purchased, created = StudentProfile.objects.get_or_create(
#                     user=request.user,
#                     defaults={'lessons_purchased': quantity}
#                 )
#                 if not created:
#                     lessons_purchased.lessons_purchased += quantity
#                     lessons_purchased.save()
            
#             # Clear the cart after successful payment
#             request.session['cart'] = {}
#             request.session['cart_count'] = 0
#             request.session.modified = True
#             return redirect('checkout_success')  # Redirect to success page

#         except stripe.error.CardError as e:
#             messages.error(request, f"Payment error: {e.user_message}")
#             return redirect('checkout')

#     # For both GET and POST, render the checkout page with `client_secret`
#     total = sum(item['price'] * item['quantity'] for item in cart.values())
#     return render(request, 'lessons/checkout.html', {
#         'cart': cart,
#         'total': total,
#         'stripe_public_key': settings.STRIPE_API_KEY,
#         'client_secret': intent.client_secret,  # Pass client secret to the template
#     })
# @login_required
# def checkout_view(request):
#     cart = request.session.get('cart', {})
#     total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
    
#     # Create a PaymentIntent to ensure `client_secret` is available
#     intent = stripe.PaymentIntent.create(
#         amount=int(total_amount * 100),  # Stripe expects the amount in cents
#         currency="usd",
#     )
    
#     if request.method == 'POST':
#         try:
#             # Confirm the PaymentIntent
#             stripe.PaymentIntent.confirm(
#                 intent.id,
#                 payment_method=request.POST['payment_method_id']
#             )

#             # Update lessons_purchased in StudentProfile
#             for lesson_id, item in cart.items():
#                 quantity = item['quantity']
#                 lessons_purchased, created = StudentProfile.objects.get_or_create(
#                     user=request.user,
#                     defaults={'lessons_purchased': quantity}
#                 )
#                 if not created:
#                     lessons_purchased.lessons_purchased += quantity
#                     lessons_purchased.save()
            
#             # Clear the cart after successful payment
#             request.session['cart'] = {}
#             request.session['cart_count'] = 0
#             request.session.modified = True
#             return redirect('checkout_success')  # Redirect to success page

#         except stripe.error.CardError as e:
#             messages.error(request, f"Payment error: {e.user_message}")
#             return redirect('checkout')

#     # For GET and POST, render the checkout page with `client_secret`
#     total = sum(item['price'] * item['quantity'] for item in cart.values())
#     return render(request, 'lessons/checkout.html', {
#         'cart': cart,
#         'total': total,
#         'stripe_public_key': settings.STRIPE_API_KEY,
#         'client_secret': intent.client_secret,  # Pass client secret to the template
#     })
# @login_required
# def checkout_view(request):
#     cart = request.session.get('cart', {})
    
#     if request.method == 'POST':
#         # Stripe payment processing
#         total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
#         try:
#             stripe.PaymentIntent.create(
#                 amount=int(total_amount * 100),  # Stripe expects the amount in cents
#                 currency="usd",
#                 payment_method=request.POST['payment_method_id'],
#                 confirm=True
#             )
            
#             # Update the lessons_purchased field in StudentProfile
#             # Update the cart count in the session based on the current cart contents
#             request.session['cart_count'] = sum(item['quantity'] for item in cart.values())
#             request.session.modified = True  # Ensure session data is saved
#             # Update or create UserCredits entries
#             for lesson_id, item in cart.items():
#                 quantity = item['quantity']
        
#                 lessons_purchased, created = StudentProfile.objects.get_or_create(
#                 user=request.user,
#                 defaults={'lessons_purchased': quantity}
#                 )
#             if not created:
#                 lessons_purchased.lessons_purchased += quantity
#                 lessons_purchased.save()    
#             request.session['lessons_purchased'] = request.session['lessons_purchased'] + quantity
        
#             # Clear the cart after successful payment
#             request.session['cart'] = {}
#             request.session['cart_count'] = 0
#             request.session.modified = True
#             return redirect('profile')

#         except stripe.error.CardError as e:
#             messages.error(request, f"Payment error: {e.user_message}")
#             return redirect('checkout')

#     total = sum(item['price'] * item['quantity'] for item in cart.values())
#     line_items = [
#         {
#             'price_data': {
#                 'currency': 'usd',
#                 'product_data': {
#                     'name': item['name'],
#                 },
#                 'unit_amount': int(item['price'] * 100),  # Amount in cents
#             },
#             'quantity': item['quantity'],
#         }
#         for item in cart.values()
#     ]

#     # Create a Stripe checkout session
#     session = stripe.checkout.Session.create(
#         payment_method_types=['card'],
#         line_items=line_items,
#         mode='payment',
#         success_url=request.build_absolute_uri('/profile/'),
#         cancel_url=request.build_absolute_uri('/profile/'),
#     )

#     return render(request, 'lessons/checkout.html', {
#         'cart': cart,
#         'total': total,
#         'stripe_public_key': settings.STRIPE_API_KEY,
#         'checkout_session_id': session.id,
#     }
#     )
@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # Create a PaymentIntent and pass `client_secret` to template
    intent = stripe.PaymentIntent.create(
        amount=int(total_amount * 100),  # Stripe expects amount in cents
        currency="usd",
        automatic_payment_methods={"enabled": True},  # Enables automatic methods, including Link
        #payment_method_options={"link": {"enabled": False}},
    )
    
    # Calculate total for display in the template
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    return render(request, 'lessons/checkout.html', {
        'cart': cart,
        'total': total,
        'stripe_public_key': settings.STRIPE_API_KEY,
        'client_secret': intent.client_secret,  # Pass client secret to the template
    })

@login_required
def checkout_success(request):
    cart = request.session.get('cart', {})
    total_lessons = 0  # Track the total lessons purchased for the email message

    # Update `lessons_purchased` field in StudentProfile
    for lesson_id, item in cart.items():
        quantity = item['quantity']
        total_lessons += quantity  # Add to total lessons for the email message
        profile, created = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={'lessons_purchased': quantity}
        )
        if not created:
            profile.lessons_purchased += quantity
            profile.lesson_history = []
            profile.save()

    # Clear the cart after updating lessons
    request.session['cart'] = {}
    request.session['cart_count'] = 0
    request.session.modified = True

    # Send email notification
    send_purchase_email(request.user, total_lessons)

    messages.success(request, "Thank you for your purchase! Your lessons have been added.")
    return redirect('profile')

def send_purchase_email(user, total_lessons):
    subject = "Your Lesson Purchase Confirmation"
    message = (
        f"Dear {user.first_name},\n\n"
        f"Thank you for your purchase! You have successfully added {total_lessons} lessons to your account.\n"
        "We look forward to helping you achieve your vocal goals.\n\n"
        "Best regards,\n"
        "Candice Meyer Vocal Studio"
    )
    recipient_email = user.email
    from_email = settings.DEFAULT_FROM_EMAIL

    # Send the email
    send_mail(
        subject,
        message,
        from_email,
        [recipient_email],
        fail_silently=False,
    )


def checkout_cancel(request):
    return render(request, 'lessons/checkout_cancel.html')
    
def student_edit(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('students'))  # Redirect to the students list after saving
    else:
        form = StudentForm(instance=student)

    return render(request, 'lessons/student_edit.html', {'form': form, 'student': student})

# Signal to create StudentProfile for each new user
@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        StudentProfile.objects.create(user=instance)

def update_cart(request, lesson_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})

        if str(lesson_id) in cart:
            if quantity > 0:
                cart[str(lesson_id)]['quantity'] = quantity
            else:
                del cart[str(lesson_id)]

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')

# # Store View
# def store_view(request):
#     student_profile = StudentProfile.objects.get(user=request.user)
#     lessons = LessonType.objects.all()
#     for lesson in lessons:
#         if lesson.duration == student_profile.lesson_duration:
#             return render(request, 'lessons/store.html', {'lesson': lesson})
#     return render(request, 'lessons/store.html', {'lessons': lessons})

def store_view(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    # Filter lessons based on the student's preferred lesson duration
    filtered_lessons = LessonType.objects.filter(duration=student_profile.lesson_duration)
    
    # If no matching lessons found, fall back to all lessons
    if not filtered_lessons.exists():
        lessons = LessonType.objects.all()
    else:
        lessons = filtered_lessons

    return render(request, 'lessons/store.html', {'lessons': lessons})


# Signal for Profile Creation
@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        StudentProfile.objects.create(user=instance)

# lessons/views.py
def email(request):
    # This is a placeholder view for the "email" page
    return render(request, 'lessons/email.html')

def lesson_list(request):
    lessons = LessonType.objects.all()
    return render(request, 'lessons/lesson_list.html', {'lessons': lessons})
