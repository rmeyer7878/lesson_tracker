# lessons/urls.py
from django.urls import path
from . import views
from django.contrib.auth.decorators import user_passes_test

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('email/', views.email, name='email'),

    # Student management - Only accessible by superusers
    path('students/', user_passes_test(lambda u: u.is_superuser)(views.student_list), name='students'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),  # Detail view
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),  # Edit view
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),  # Delete view
    path('students/<int:pk>/lessons/', views.student_lessons, name='student_lessons'),  # List student's lessons

    # Lesson listing and purchasing
    path('lessons/', views.lesson_list, name='lesson_list'),  # List of all available lessons
    path('purchase_more/', views.purchase_more, name='purchase_more'),  # Purchase additional lessons
    path('purchase/', views.purchase_lessons, name='purchase_lessons'),  # Main purchase page
    path('purchase/success/', views.purchase_success, name='purchase_success'),  # Success page
    path('purchase/cancel/', views.purchase_cancel, name='purchase_cancel'),  # Cancel page
    path('paypal/', views.paypal, name='paypal'),  # PayPal payment page

    # Lesson details and store
    path('store/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),  # Detailed view of a lesson type
    path('store/', views.store_view, name='store'),  # Store listing all available lessons
    
    # User profile
    path('profile/', views.profile, name='profile'),  # User profile page

    # Cart and checkout
    path('cart/', views.cart_view, name='cart'),  # View cart
    path('add-to-cart/<int:lesson_id>/', views.add_to_cart, name='add_to_cart'),  # Add a lesson to cart
    path('update-cart/<int:lesson_id>/', views.update_cart, name='update_cart'),  # Update cart item quantity
    path('checkout/', views.checkout_view, name='checkout'),  # Checkout page
]
