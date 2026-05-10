"""
URL Configuration for users app.
"""
from django.urls import path
from apps.users import views
from apps.users.forms import UserLoginForm

app_name = 'users'

urlpatterns = [
    # Guest Authentication
    path('register/', views.GuestRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Staff Authentication
    path('staff-login/', views.UserLoginView.as_view(
        template_name='staff/login.html',
        form_class=UserLoginForm
    ), name='staff_login'),
    
    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]