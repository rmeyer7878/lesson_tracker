# lessons/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Student, LessonType, StudentLesson
from .forms import PurchaseLessonForm, StudentForm, LessonForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    return render(request, 'lessons/home.html')

def about(request):
    return render(request, 'lessons/about.html')

@login_required
def student_list(request):
    if not request.user.is_superuser:
        return redirect('home')
    students = Student.objects.all()
    return render(request, 'lessons/student_list.html', {'students': students})

def email(request):
    return render(request, 'lessons/email.html')

def lesson_list(request):
    lessons = LessonType.objects.all()
    return render(request, 'lessons/lesson_list.html', {'lessons': lessons})

def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(LessonType, id=lesson_id)
    return render(request, 'lessons/lesson_detail.html', {'lesson': lesson})

def purchase_lessons(request):
    lesson_types = LessonType.objects.all()
    return render(request, 'lessons/purchase_lessons.html', {'lesson_types': lesson_types})

def purchase_more(request):
    if request.method == 'POST':
        form = PurchaseLessonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students')
    else:
        form = PurchaseLessonForm()
    return render(request, 'lessons/purchase_more.html', {'form': form})

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'lessons/student_detail.html', {'student': student})

def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('students')
    else:
        form = StudentForm(instance=student)
    return render(request, 'lessons/student_edit.html', {'form': form, 'student': student})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('students')
    return render(request, 'lessons/student_confirm_delete.html', {'student': student})

def student_lessons(request, pk):
    student = get_object_or_404(Student, pk=pk)
    lessons = student.lessons.all()

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.student = student
            lesson.save()
            return redirect('student_lessons', pk=student.pk)
    else:
        form = LessonForm()

    return render(request, 'lessons/student_lessons.html', {
        'student': student,
        'lessons': lessons,
        'form': form,
    })

@login_required
def profile(request):
    try:
        student = Student.objects.get(user=request.user)
        student_lessons = StudentLesson.objects.filter(student=student)  # Get all lesson types for the student
    except Student.DoesNotExist:
        return render(request, 'lessons/no_profile.html')  # Customize as needed

    return render(request, 'lessons/profile.html', {'student': student, 'student_lessons': student_lessons})

def paypal(request):
    return render(request, 'lessons/paypal.html')

def purchase_success(request):
    return render(request, 'lessons/purchase_success.html')

def purchase_cancel(request):
    return render(request, 'lessons/purchase_cancel.html')

def cart_view(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'lessons/cart.html', {'cart': cart, 'total': total})

def add_to_cart(request, lesson_id):
    lesson = get_object_or_404(LessonType, id=lesson_id)
    
    # Get the cart from session or initialize it as an empty dictionary
    cart = request.session.get('cart', {})

    # Check if the lesson is already in the cart
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

    # Save the updated cart to the session
    request.session['cart'] = cart
    request.session.modified = True  # Mark the session as modified to ensure it’s saved

    return redirect('store')  # Redirect to the store or another page after adding to cart

@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('store')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "No student profile found.")
        return redirect('store')

    for lesson_id, item in cart.items():
        lesson_type = get_object_or_404(LessonType, id=lesson_id)
        quantity = item['quantity']
        
        # Get or create a StudentLesson entry for the student and lesson type
        student_lesson, created = StudentLesson.objects.get_or_create(
            student=student,
            lesson_type=lesson_type
        )
        
        # Increase the lesson count
        student_lesson.quantity += quantity
        student_lesson.save()

    # Clear the cart after checkout
    request.session['cart'] = {}
    request.session.modified = True

    messages.success(request, "Checkout complete! Your lessons have been added to your account.")
    return redirect('profile')


# @login_required
# def checkout_view(request):
#     cart = request.session.get('cart', {})
    
#     if not cart:
#         messages.warning(request, "Your cart is empty.")
#         return redirect('store')

#     student = Student.objects.get(user=request.user)

#     # Loop through the cart and update the student's lessons
#     for lesson_id, item in cart.items():
#         try:
#             lesson_type = LessonType.objects.get(id=lesson_id)
#             # Assuming `student` has a `lessons_left` or similar field to track purchased lessons
#             student.lessons_left += item['quantity']  # Increase total lessons based on cart quantity
#             student.save()
#         except LessonType.DoesNotExist:
#             messages.error(request, "Lesson type not found.")
#             continue

#     # Clear the cart after checkout
#     request.session['cart'] = {}
#     request.session.modified = True

#     messages.success(request, "Checkout completed successfully, and your lessons have been added.")
#     return render(request, 'lessons/checkout_success.html')




def store_view(request):
    lessons = LessonType.objects.all()
    return render(request, 'lessons/store.html', {'lessons': lessons})

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
