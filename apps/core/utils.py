"""
Utility functions for VETA Hotel Booking System.
"""
import random
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import Q


def generate_reference_id():
    """
    Generate a unique booking reference ID.
    Format: VETA-YYYY-NNNN (e.g., VETA-2026-0042)
    
    Returns:
        str: Unique reference ID
    """
    year = datetime.now().year
    sequence = str(random.randint(1, 9999)).zfill(4)
    return f"VETA-{year}-{sequence}"


def calculate_nights(check_in, check_out):
    """
    Calculate number of nights between two dates.
    
    Args:
        check_in (date): Check-in date
        check_out (date): Check-out date
    
    Returns:
        int: Number of nights
    """
    if check_in and check_out:
        delta = check_out - check_in
        return max(delta.days, 1)  # Minimum 1 night
    return 0


def format_currency_tzs(amount):
    """
    Format amount in Tanzanian Shillings.
    
    Args:
        amount (decimal): Amount in TZS
    
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return "TZS 0"
    return f"TZS {int(amount):,}"


def get_date_range_display(check_in, check_out):
    """
    Get a human-readable date range string.
    
    Args:
        check_in (date): Start date
        check_out (date): End date
    
    Returns:
        str: Formatted date range
    """
    date_format = "%d %b %Y"
    return f"{check_in.strftime(date_format)} → {check_out.strftime(date_format)}"


def search_bookings_by_guest(query):
    """
    Search bookings by guest phone or reference ID.
    
    Args:
        query (str): Phone number or reference ID
    
    Returns:
        QuerySet: Matching bookings with related data
    """
    from apps.bookings.models import Booking
    
    return Booking.objects.filter(
        Q(reference_id__icontains=query) |
        Q(guest__phone__icontains=query)
    ).select_related(
        'guest', 'room', 'processed_by'
    ).order_by('-created_at')


def get_today():
    """Get current date in the system timezone."""
    return timezone.now().date()


def get_tomorrow():
    """Get tomorrow's date."""
    return get_today() + timedelta(days=1)


def get_date_range_from_request(request):
    """
    Extract check-in and check-out dates from request parameters.
    
    Args:
        request: HTTP request object
    
    Returns:
        tuple: (check_in, check_out) dates
    """
    from datetime import datetime
    
    check_in_str = request.GET.get('check_in', '')
    check_out_str = request.GET.get('check_out', '')
    
    check_in = None
    check_out = None
    
    if check_in_str:
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if check_out_str:
        try:
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Set defaults if not provided
    if not check_in:
        check_in = get_today()
    if not check_out:
        check_out = get_tomorrow()
    
    return check_in, check_out