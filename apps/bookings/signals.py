"""
Signals for booking app.
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from apps.bookings.models import Booking


@receiver(post_save, sender=Booking)
def update_room_status_on_booking(sender, instance, created, **kwargs):
    """
    Update room status when booking is created or modified.
    """
    if created:
        # If booking is pending and room is available
        if instance.status == 'pending' and instance.room.status == 'available':
            # Room stays available until booking is approved
            pass


@receiver(post_save, sender=Booking)
def handle_booking_cancellation(sender, instance, **kwargs):
    """
    Handle side effects when booking is cancelled.
    """
    if instance.status == 'cancelled':
        # If room was reserved for this booking, make it available
        if instance.room.status == 'reserved':
            # Check if there are other active bookings for this room
            active_bookings = instance.room.bookings.filter(
                status__in=['approved', 'checked_in']
            ).exclude(id=instance.id).exists()
            
            if not active_bookings:
                instance.room.update_status('available')


@receiver(post_save, sender=Booking)
def handle_booking_checkout(sender, instance, **kwargs):
    """
    Handle side effects when guest checks out.
    """
    if instance.status == 'checked_out':
        # Room becomes available
        active_bookings = instance.room.bookings.filter(
            status__in=['approved', 'checked_in']
        ).exclude(id=instance.id).exists()
        
        if not active_bookings:
            instance.room.update_status('available')