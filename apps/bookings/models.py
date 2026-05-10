"""
Booking models for VETA Hotel Booking System.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from apps.core.models import TimeStampedModel
from apps.core.constants import BOOKING_STATUS, PAYMENT_STATUS
from apps.core.utils import generate_reference_id, calculate_nights, format_currency_tzs


class Booking(TimeStampedModel):
    """
    Core booking model for the hotel system.
    Tracks the entire booking lifecycle.
    """
    STATUS_CHOICES = BOOKING_STATUS
    PAYMENT_CHOICES = PAYMENT_STATUS
    
    # Reference and Identification
    reference_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Unique booking reference (e.g., VETA-2026-0042)"
    )
    
    # Relationships
    guest = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='bookings',
        help_text="Guest who made the booking"
    )
    
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.PROTECT,
        related_name='bookings',
        help_text="Booked room"
    )
    
    # Dates
    check_in = models.DateField(
        help_text="Check-in date"
    )
    check_out = models.DateField(
        help_text="Check-out date"
    )
    nights = models.IntegerField(
        editable=False,
        validators=[MinValueValidator(1)],
        help_text="Number of nights"
    )
    
    # Financial
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text="Room price at time of booking"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text="Total amount in TZS"
    )
    
    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current booking status"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='unpaid',
        db_index=True,
        help_text="Payment status"
    )
    
    # Timestamps for tracking
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Staff processing
    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_bookings',
        help_text="Staff member who processed the booking"
    )
    
    # Guest Details
    guest_count = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of guests"
    )
    special_requests = models.TextField(
        blank=True,
        help_text="Special requests from guest"
    )
    
    # Cancellation
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Reason for cancellation"
    )
    
    # Notes (internal, not visible to guest)
    staff_notes = models.TextField(
        blank=True,
        help_text="Internal staff notes"
    )
    
    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'check_in']),
            models.Index(fields=['reference_id']),
            models.Index(fields=['guest', 'status']),
            models.Index(fields=['check_in', 'check_out']),
        ]
    
    def __str__(self):
        return f"{self.reference_id} - {self.guest.get_full_name()} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate nights and total amount."""
        if not self.reference_id:
            self.reference_id = generate_reference_id()
        
        # Calculate nights
        self.nights = calculate_nights(self.check_in, self.check_out)
        
        # Save price at time of booking
        if not self.price_per_night:
            self.price_per_night = self.room.price_per_night
        
        # Calculate total
        self.total_amount = self.price_per_night * self.nights
        
        super().save(*args, **kwargs)
    
    def get_total_display(self):
        """Return formatted total amount."""
        return format_currency_tzs(self.total_amount)
    
    def get_price_per_night_display(self):
        """Return formatted price per night."""
        return format_currency_tzs(self.price_per_night)
    
    def get_status_badge_class(self):
        """Return CSS class for status badge."""
        classes = {
            'pending': 'warning',
            'approved': 'info',
            'checked_in': 'primary',
            'checked_out': 'success',
            'cancelled': 'danger',
        }
        return classes.get(self.status, 'secondary')
    
    def get_payment_badge_class(self):
        """Return CSS class for payment badge."""
        classes = {
            'unpaid': 'danger',
            'paid': 'success',
            'partial': 'warning',
            'refunded': 'info',
        }
        return classes.get(self.payment_status, 'secondary')
    
    @property
    def is_active(self):
        """Check if booking is active (not cancelled or checked out)."""
        return self.status not in ['cancelled', 'checked_out']
    
    @property
    def can_approve(self):
        """Check if booking can be approved."""
        return self.status == 'pending'
    
    @property
    def can_cancel(self):
        """Check if booking can be cancelled."""
        return self.status in ['pending', 'approved']
    
    @property
    def can_check_in(self):
        """Check if guest can check in."""
        return self.status == 'approved' and self.payment_status == 'paid'
    
    @property
    def can_check_out(self):
        """Check if guest can check out."""
        return self.status == 'checked_in'
    
    def approve(self, staff_user):
        """Approve a pending booking."""
        if not self.can_approve:
            raise ValueError(f"Cannot approve booking with status: {self.status}")
        
        self.status = 'approved'
        self.approved_at = timezone.now()
        self.processed_by = staff_user
        self.save()
        return True
    
    def cancel(self, reason='', cancelled_by=None):
        """Cancel a booking."""
        if not self.can_cancel:
            raise ValueError(f"Cannot cancel booking with status: {self.status}")
        
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        
        if cancelled_by:
            self.processed_by = cancelled_by
        
        self.save()
        
        # Update room status if needed
        if self.room.status == 'reserved':
            self.room.update_status('available')
        
        return True
    
    def check_in_guest(self, staff_user):
        """Process guest check-in."""
        if not self.can_check_in:
            raise ValueError(f"Cannot check in booking with status: {self.status}")
        
        self.status = 'checked_in'
        self.checked_in_at = timezone.now()
        self.processed_by = staff_user
        self.save()
        
        # Update room status
        self.room.update_status('occupied')
        
        return True
    
    def check_out_guest(self, staff_user):
        """Process guest check-out."""
        if not self.can_check_out:
            raise ValueError(f"Cannot check out booking with status: {self.status}")
        
        self.status = 'checked_out'
        self.checked_out_at = timezone.now()
        self.processed_by = staff_user
        self.save()
        
        # Update room status
        self.room.update_status('available')
        
        return True
    
    def mark_as_paid(self, staff_user):
        """Mark booking as paid."""
        if self.payment_status == 'paid':
            raise ValueError("Booking is already marked as paid")
        
        self.payment_status = 'paid'
        self.paid_at = timezone.now()
        self.processed_by = staff_user
        self.save()
        return True
    
    def get_duration_display(self):
        """Return human-readable duration."""
        if self.nights == 1:
            return "1 night"
        return f"{self.nights} nights"
    
    def get_dates_display(self):
        """Return formatted date range."""
        from apps.core.utils import get_date_range_display
        return get_date_range_display(self.check_in, self.check_out)
    
    def get_timeline(self):
        """Return booking timeline events."""
        events = [
            {'time': self.created_at, 'event': 'Booking Created', 'icon': 'plus-circle'},
        ]
        
        if self.approved_at:
            events.append({'time': self.approved_at, 'event': 'Booking Approved', 'icon': 'check-circle'})
        
        if self.paid_at:
            events.append({'time': self.paid_at, 'event': 'Payment Received', 'icon': 'dollar-sign'})
        
        if self.checked_in_at:
            events.append({'time': self.checked_in_at, 'event': 'Guest Checked In', 'icon': 'sign-in'})
        
        if self.checked_out_at:
            events.append({'time': self.checked_out_at, 'event': 'Guest Checked Out', 'icon': 'sign-out'})
        
        if self.cancelled_at:
            events.append({'time': self.cancelled_at, 'event': 'Booking Cancelled', 'icon': 'times-circle'})
        
        return sorted(events, key=lambda x: x['time'])