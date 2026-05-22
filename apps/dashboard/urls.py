"""
URL Configuration for dashboard app.
"""
from django.urls import path
from apps.dashboard import views

app_name = 'dashboard'

urlpatterns = [
    # Staff Dashboard
    path('', views.dashboard, name='index'),
    
    # Manager Dashboard
    path('manager/', views.manager_dashboard, name='manager_index'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    
    # Quick Search
    path('quick-search/', views.quick_search, name='quick_search'),
    
    # Staff Management
    path('staff-list/', views.staff_list, name='staff_list'),
    path('staff/create/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('staff/<int:pk>/edit/', views.staff_edit, name='staff_edit'),
    path('staff/<int:pk>/toggle/', views.staff_toggle, name='staff_toggle'),
    
    # Guest List
    path('guest-list/', views.guest_list, name='guest_list'),
    path('user/<int:pk>/', views.user_detail, name='user_detail'),
    
    # AJAX Endpoints
    path('api/realtime-stats/', views.get_realtime_stats, name='realtime_stats'),
]