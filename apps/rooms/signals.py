"""
Signals for rooms app.
"""
from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.rooms.models import Room
from apps.core.constants import ROOM_STATUS


@receiver(pre_save, sender=Room)
def validate_room_status_change(sender, instance, **kwargs):
    """
    Validate room status changes and handle side effects.
    """
    if instance.pk:
        try:
            old_instance = Room.objects.get(pk=instance.pk)
            
            # If room is being set to available and has active bookings
            if instance.status == 'available' and old_instance.status == 'occupied':
                active_bookings = instance.bookings.filter(
                    status__in=['approved', 'checked_in']
                ).exists()
                
                if active_bookings:
                    # Cannot set to available if there are active bookings
                    raise ValueError(
                        f"Cannot set Room {instance.room_number} to available. "
                        "There are active bookings for this room."
                    )
        except Room.DoesNotExist:
            pass