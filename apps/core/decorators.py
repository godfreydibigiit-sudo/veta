"""
Custom decorators for access control in VETA Hotel Booking System.
"""
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def staff_required(view_func=None, redirect_url='staff:login'):
    """
    Decorator for views that require staff or admin access.
    Redirects to staff login page if user is not staff.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access the staff area.')
                return redirect(redirect_url)
            
            if not hasattr(request.user, 'is_staff_user') or not request.user.is_staff_user():
                messages.error(request, 'You do not have permission to access this area.')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func is None:
        return decorator
    return decorator(view_func)


def guest_required(view_func=None):
    """
    Decorator for views that require guest access.
    Ensures only registered guests can access certain views.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please login to continue.')
                return redirect('users:login')
            
            if request.user.role != 'guest':
                messages.error(request, 'Staff members cannot access this area.')
                return redirect('staff:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func is None:
        return decorator
    return decorator(view_func)


def ajax_required(view_func):
    """
    Decorator for AJAX-only views.
    Returns 400 error if request is not AJAX.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest('Invalid request')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def manager_required(view_func=None, redirect_url='users:staff_login'):
    """
    Decorator for views that require manager or admin access.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this area.')
                return redirect(redirect_url)
            
            if not request.user.is_staff_user():
                messages.error(request, 'You do not have permission to access this area.')
                return redirect('home')
            
            if not request.user.can_manage_staff():
                messages.error(request, 'Only managers can access this area.')
                return redirect('dashboard:index')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func is None:
        return decorator
    return decorator(view_func)