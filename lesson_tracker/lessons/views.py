# lessons/views.py

import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import StudentProfile, LessonType, UserCredits, RecurringLesson
from .forms import PurchaseLessonForm, StudentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect

stripe.api_key = settings.SECRET_KEY

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
    # Get the credits for each lesson type, sorted by lesson type name
    credits = UserCredits.objects.filter(user=request.user).order_by('lesson_type__name')
    # Get the recurring weekly lesson for the user
    recurring_lesson = RecurringLesson.objects.filter(user=request.user).first()

    return render(request, 'lessons/profile.html', {
        'credits': credits,
        'recurring_lesson': recurring_lesson
    })

# def profile(request):
#     # Get all students linked to the logged-in user
#     credits = UserCredits.objects.filter(user=request.user)
#     students = Student.objects.filter(user=request.user)
#     next_lesson = ScheduledLesson.objects.filter(user=request.user, is_cancelled=False).order_by('scheduled_time').first()
    
#     # Get all StudentLesson instances for these students
#     #student_lessons = StudentLesson.objects.filter(student__in=students)
#     student_lessons = StudentLesson.objects.filter(student=request.user).select_related('lesson_type')

#     return render(request, 'lessons/profile.html', {
#         'students': students,
#         'student_lessons': student_lessons,
#         'credits': credits, 
#         'next_lesson': next_lesson
#     })


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

@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if request.method == 'POST':
        # Stripe payment processing
        total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
        try:
            stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Stripe expects amount in cents
                currency="usd",
                payment_method=request.POST['payment_method_id'],
                confirm=True
            )
            
            # Update or create UserCredits entries
            for lesson_id, item in cart.items():
                lesson_type = get_object_or_404(LessonType, id=lesson_id)
                quantity = item['quantity']
                
                # Update credits in UserCredits
                user_credit, created = UserCredits.objects.get_or_create(
                    user=request.user,
                    lesson_type=lesson_type,
                    defaults={'credits': quantity}
                )
                
                if not created:
                    user_credit.credits += quantity
                    user_credit.save()

            # Clear the cart after successful payment
            request.session['cart'] = {}
            request.session['cart_count'] = 0
            request.session.modified = True
            messages.success(request, "Checkout complete! Your credits have been updated.")
            return redirect('profile')

        except stripe.error.CardError as e:
            messages.error(request, f"Payment error: {e.user_message}")
            return redirect('checkout')

    total = sum(item['price'] * item['quantity'] for item in cart.values())
    line_items = [
        {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': int(item['price'] * 100),  # Amount in cents
            },
            'quantity': item['quantity'],
        }
        for item in cart.values()
    ]

    # Create a Stripe checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/checkout/success/'),
        cancel_url=request.build_absolute_uri('/checkout/cancel/'),
    )

    return render(request, 'lessons/checkout.html', {
        'cart': cart,
        'total': total,
        'stripe_public_key': settings.STRIPE_API_KEY,
        'checkout_session_id': session.id,
    })


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

def purchase_lesson(request, lesson_type_id):
    # Logic for payment success
    lesson_type = LessonType.objects.get(id=lesson_type_id)
    user_credit, created = UserCredits.objects.get_or_create(user=request.user, lesson_type=lesson_type)
    user_credit.credits += 1
    user_credit.save()
    messages.success(request, "Lesson purchased successfully!")
    return redirect('profile')

def checkout_success(request):
    request.session['cart'] = {}  # Clear the cart
    request.session['cart_count'] = 0
    request.session.modified = True
    messages.success(request, "Thank you! Your purchase was successful.")
    return redirect('profile')  # Redirect to the profile or another page

# Signal to create StudentProfile for each new user
@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        StudentProfile.objects.create(user=instance)

def checkout_cancel(request):
    messages.error(request, "Payment was canceled.")
    return redirect('cart')  # Redirect back to the cart

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

# Store View
def store_view(request):
    lessons = LessonType.objects.all()
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
