"""
Custom validators for VETA Hotel Booking System.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta


def validate_future_date(value):
    """
    Validate that a date is in the future.
    """
    if value < timezone.now().date():
        raise ValidationError('Date must be in the future.')


def validate_check_out_after_check_in(check_in, check_out):
    """
    Validate that check-out date is after check-in date.
    """
    if check_out <= check_in:
        raise ValidationError('Check-out date must be after check-in date.')


def validate_phone_number(value):
    """
    Validate Tanzanian phone number format.
    Accepts formats: +255XXXXXXXXX, 255XXXXXXXXX, 0XXXXXXXXX
    """
    import re
    
    # Remove spaces and special characters
    cleaned = re.sub(r'[\s\-\(\)]', '', value)
    
    # Pattern: +255XXXXXXXXX or 255XXXXXXXXX or 0XXXXXXXXX
    pattern = r'^(\+?255|0)[67]\d{8}$'
    
    if not re.match(pattern, cleaned):
        raise ValidationError(
            'Enter a valid Tanzanian phone number (e.g., +255712345678 or 0712345678).'
        )


def validate_minimum_nights(value):
    """
    Validate minimum number of nights (at least 1).
    """
    if value < 1:
        raise ValidationError('Minimum stay is 1 night.')


def validate_room_capacity(capacity, guests):
    """
    Validate number of guests doesn't exceed room capacity.
    """
    if guests > capacity:
        raise ValidationError(
            f'Room capacity is {capacity} guest(s). Cannot accommodate {guests} guests.'
        )