"""
Context processors for VETA Hotel Booking System.
"""
from django.conf import settings
from apps.core.constants import CURRENCY_SYMBOL


def veta_context(request):
    """
    Add common context variables to all templates.
    """
    context = {
        'SITE_NAME': 'VETA Hotel',
        'CURRENCY': CURRENCY_SYMBOL,
        'CURRENT_YEAR': 2026,
        'DEBUG': settings.DEBUG,
    }
    
    # Add user role context if authenticated
    if request.user.is_authenticated:
        context.update({
            'is_guest': request.user.role == 'guest',
            'is_staff': request.user.role in ['staff', 'admin'],
            'is_admin': request.user.role == 'admin',
        })
    
    return context