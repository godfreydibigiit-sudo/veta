"""
Core URL Configuration for VETA Hotel.
"""
from django.urls import path
from apps.core import views

urlpatterns = [
    path('', views.home, name='home'),
]

# Error handlers
handler404 = 'apps.core.views.custom_404'
handler500 = 'apps.core.views.custom_500'
handler403 = 'apps.core.views.custom_403'