"""
Core views for VETA Hotel Booking System.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.rooms.models import Room
from apps.bookings.models import Booking


def home(request):
    """
    Homepage view - redirects based on user role.
    Staff users go to dashboard, guests see available rooms.
    """
    if request.user.is_authenticated:
        if hasattr(request.user, 'is_staff_user') and request.user.is_staff_user():
            return redirect('dashboard:index')
    
    # Get featured/available rooms for landing page
    available_rooms = Room.objects.filter(
        status='available', 
        is_active=True
    ).order_by('?')[:6]  # Random 6 available rooms
    
    context = {
        'available_rooms': available_rooms,
        'total_rooms': Room.objects.filter(is_active=True).count(),
        'active_bookings': Booking.objects.filter(
            status__in=['approved', 'checked_in']
        ).count(),
    }
    
    return render(request, 'guest/home.html', context)


def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """Custom 500 error page"""
    return render(request, 'errors/500.html', status=500)


def custom_403(request, exception):
    """Custom 403 error page"""
    return render(request, 'errors/403.html', status=403)