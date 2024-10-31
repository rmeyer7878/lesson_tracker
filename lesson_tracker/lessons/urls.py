from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required, user_passes_test

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('email/', views.email, name='email'),

    # Student management - Only accessible by superusers
    path('students/', user_passes_test(lambda u: u.is_superuser)(views.student_list), name='students'),
    path('students/<int:pk>/', user_passes_test(lambda u: u.is_superuser)(views.student_detail), name='student_detail'),  
    path('students/<int:pk>/edit/', user_passes_test(lambda u: u.is_superuser)(views.student_edit), name='student_edit'),
    path('students/<int:pk>/delete/', user_passes_test(lambda u: u.is_superuser)(views.student_delete), name='student_delete'),  
    path('students/<int:pk>/lessons/', user_passes_test(lambda u: u.is_superuser)(views.student_lessons), name='student_lessons'),

    # Lesson listing and purchasing
    path('lessons/', views.lesson_list, name='lesson_list'),  # List of all available lessons
    path('purchase/', views.purchase_lesson, name='purchase_lesson'),  # Main purchase page for selecting lessons

    # Store page, if separate from lesson listing
    path('store/', views.store_view, name='store'),  # Store listing all available lessons
    
    # User profile - Accessible only to logged-in users
    path('profile/', login_required(views.profile), name='profile'),  # User profile page

    # Cart and checkout - Also restricted to logged-in users
    path('cart/', login_required(views.cart_view), name='cart'),  # View cart
    path('add-to-cart/<int:lesson_id>/', login_required(views.add_to_cart), name='add_to_cart'),  # Add a lesson to cart
    path('update-cart/<int:lesson_id>/', login_required(views.update_cart), name='update_cart'),  # Update cart item quantity
    path('checkout/', login_required(views.checkout_view), name='checkout'),  # Checkout page
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
]
