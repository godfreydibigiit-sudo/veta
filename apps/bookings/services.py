"""
Business logic services for bookings.
"""
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from apps.bookings.models import Booking
from apps.rooms.models import Room
from apps.core.utils import generate_reference_id


class BookingService:
    """
    Service class for booking business logic.
    Centralizes all booking operations.
    """
    
    @staticmethod
    def is_room_available(room, check_in, check_out, exclude_booking=None):
        """
        Check if a room is available for the given dates.
        
        Args:
            room: Room instance
            check_in: Check-in date
            check_out: Check-out date
            exclude_booking: Booking instance to exclude (for updates)
        
        Returns:
            bool: True if room is available
        """
        # Basic availability checks
        if not room.is_active:
            return False, "Room is not active"
        
        if room.status == 'maintenance':
            return False, "Room is under maintenance"
        
        # Check for conflicting bookings
        query = Q(
            status__in=['pending', 'approved', 'checked_in']
        ) & Q(
            check_in__lt=check_out
        ) & Q(
            check_out__gt=check_in
        )
        
        if exclude_booking:
            query &= ~Q(id=exclude_booking.id)
        
        conflicting = room.bookings.filter(query).exists()
        
        if conflicting:
            return False, "Room is already booked for these dates"
        
        return True, "Room is available"
    
    @staticmethod
    @transaction.atomic
    def create_booking(guest, room, check_in, check_out, guest_count=1, 
                      special_requests=''):
        """
        Create a new booking with validation.
        
        Args:
            guest: User instance (guest)
            room: Room instance
            check_in: Check-in date
            check_out: Check-out date
            guest_count: Number of guests
            special_requests: Special requests text
        
        Returns:
            Booking instance or raises ValueError
        """
        # Validate guest count
        if guest_count > room.capacity:
            raise ValueError(
                f"Room capacity is {room.capacity}. Cannot accommodate {guest_count} guests."
            )
        
        # Check availability
        available, message = BookingService.is_room_available(
            room, check_in, check_out
        )
        
        if not available:
            raise ValueError(message)
        
        # Create booking
        booking = Booking.objects.create(
            guest=guest,
            room=room,
            check_in=check_in,
            check_out=check_out,
            guest_count=guest_count,
            special_requests=special_requests,
            price_per_night=room.price_per_night,
            status='pending',
            payment_status='unpaid'
        )
        
        return booking
    
    @staticmethod
    @transaction.atomic
    def approve_booking(booking, staff_user):
        """
        Approve a pending booking.
        
        Args:
            booking: Booking instance
            staff_user: Staff user approving
        
        Returns:
            Booking instance
        """
        if not booking.can_approve:
            raise ValueError(f"Cannot approve booking with status: {booking.status}")
        
        booking.approve(staff_user)
        
        # Update room status to reserved
        if booking.room.status == 'available':
            booking.room.update_status('reserved')
        
        return booking
    
    @staticmethod
    @transaction.atomic
    def cancel_booking(booking, reason='', cancelled_by=None):
        """
        Cancel a booking.
        
        Args:
            booking: Booking instance
            reason: Cancellation reason
            cancelled_by: User cancelling (guest or staff)
        
        Returns:
            Booking instance
        """
        if not booking.can_cancel:
            raise ValueError(f"Cannot cancel booking with status: {booking.status}")
        
        return booking.cancel(reason, cancelled_by)
    
    @staticmethod
    @transaction.atomic
    def process_payment(booking, staff_user):
        """
        Process payment for a booking.
        
        Args:
            booking: Booking instance
            staff_user: Staff processing payment
        
        Returns:
            Booking instance
        """
        if booking.payment_status == 'paid':
            raise ValueError("Payment has already been processed")
        
        booking.mark_as_paid(staff_user)
        return booking
    
    @staticmethod
    @transaction.atomic
    def check_in(booking, staff_user):
        """
        Process guest check-in.
        
        Args:
            booking: Booking instance (must be approved and paid)
            staff_user: Staff processing check-in
        
        Returns:
            Booking instance
        """
        if booking.payment_status != 'paid':
            raise ValueError("Payment must be completed before check-in")
        
        booking.check_in_guest(staff_user)
        return booking
    
    @staticmethod
    @transaction.atomic
    def check_out(booking, staff_user):
        """
        Process guest check-out.
        
        Args:
            booking: Booking instance (must be checked in)
            staff_user: Staff processing check-out
        
        Returns:
            Booking instance
        """
        booking.check_out_guest(staff_user)
        return booking
    
    @staticmethod
    def get_active_bookings():
        """Get all currently active bookings."""
        return Booking.objects.filter(
            status__in=['pending', 'approved', 'checked_in']
        ).select_related('guest', 'room')
    
    @staticmethod
    def get_bookings_for_date(date):
        """
        Get bookings for a specific date.
        
        Args:
            date: Date to check
        
        Returns:
            QuerySet of bookings
        """
        return Booking.objects.filter(
            Q(check_in__lte=date) & Q(check_out__gte=date),
            status__in=['approved', 'checked_in']
        ).select_related('guest', 'room')
    
    @staticmethod
    def search_bookings(query):
        """
        Search bookings by reference ID, guest name, or phone.
        
        Args:
            query: Search string
        
        Returns:
            QuerySet of matching bookings
        """
        return Booking.objects.filter(
            Q(reference_id__icontains=query) |
            Q(guest__first_name__icontains=query) |
            Q(guest__last_name__icontains=query) |
            Q(guest__phone__icontains=query) |
            Q(guest__email__icontains=query)
        ).select_related('guest', 'room', 'processed_by')
    
    @staticmethod
    def get_booking_stats():
        """
        Get booking statistics for dashboard.
        
        Returns:
            dict: Statistics data
        """
        from django.db.models import Sum, Count
        
        today = timezone.now().date()
        
        return {
            'total_bookings': Booking.objects.count(),
            'pending_bookings': Booking.objects.filter(status='pending').count(),
            'approved_bookings': Booking.objects.filter(status='approved').count(),
            'checked_in': Booking.objects.filter(status='checked_in').count(),
            'checked_out_today': Booking.objects.filter(
                status='checked_out',
                checked_out_at__date=today
            ).count(),
            'total_revenue': Booking.objects.filter(
                payment_status='paid'
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0,
            'today_check_ins': Booking.objects.filter(
                status='checked_in',
                check_in=today
            ).count(),
            'today_check_outs': Booking.objects.filter(
                status__in=['approved', 'checked_in'],
                check_out=today
            ).count(),
        }