"""
URL Configuration for dashboard app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from apps.dashboard import views

app_name = 'dashboard'

urlpatterns = [
    # Main Dashboard
    path('', views.dashboard, name='index'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    
    # Quick Search
    path('quick-search/', views.quick_search, name='quick_search'),
    
    # AJAX Endpoints
    path('api/realtime-stats/', views.get_realtime_stats, name='realtime_stats'),
]