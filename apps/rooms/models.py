"""
Room models for VETA Hotel Booking System.
"""
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import TimeStampedModel, SoftDeleteModel
from apps.core.constants import ROOM_TYPES, ROOM_STATUS
from apps.core.utils import format_currency_tzs


class RoomType(models.Model):
    """
    Room type definition.
    """
    name = models.CharField(max_length=50, choices=ROOM_TYPES, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    base_capacity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    max_capacity = models.IntegerField(default=2, validators=[MinValueValidator(1)])
    amenities = models.TextField(
        blank=True,
        help_text="Separate amenities with commas (e.g., WiFi, TV, AC)"
    )
    
    class Meta:
        db_table = 'room_types'
        verbose_name = 'Room Type'
        verbose_name_plural = 'Room Types'
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()
    
    def get_amenities_list(self):
        """Return amenities as a list."""
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []


class Room(TimeStampedModel, SoftDeleteModel):
    """
    Room model with essential fields only.
    """
    ROOM_TYPE_CHOICES = ROOM_TYPES
    STATUS_CHOICES = ROOM_STATUS
    
    # Basic Information
    room_number = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="Room number or identifier"
    )
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        db_index=True,
        help_text="Type of room"
    )
    floor = models.IntegerField(
        default=1,
        help_text="Floor number"
    )
    
    # Pricing
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per night in TZS"
    )
    
    # Capacity and Features
    capacity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of guests"
    )
    description = models.TextField(
        blank=True,
        help_text="Room description and features"
    )
    
    # Image
    image = models.ImageField(
        upload_to='rooms/',
        blank=True,
        null=True,
        help_text="Room photo (optional)"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        db_index=True,
        help_text="Current room status"
    )
    
    # Additional Info
    notes = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to guests)"
    )
    
    class Meta:
        db_table = 'rooms'
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['floor', 'room_number']
        indexes = [
            models.Index(fields=['status', 'room_type']),
            models.Index(fields=['price_per_night']),
        ]
    
    def __str__(self):
        price = format_currency_tzs(self.price_per_night)
        return f"Room {self.room_number} - {self.get_room_type_display()} ({price}/night)"
    
    def get_price_display(self):
        """Return formatted price."""
        return format_currency_tzs(self.price_per_night)
    
    def get_image_url(self):
        """Return room image URL or default placeholder."""
        if self.image:
            return self.image.url
        return '/static/images/rooms/default-room.jpg'
    
    @property
    def is_available(self):
        """Check if room is available for booking."""
        return self.status == 'available' and self.is_active
    
    @property
    def is_occupied(self):
        """Check if room is currently occupied."""
        return self.status == 'occupied'
    
    def get_current_booking(self):
        """Get current active booking for this room."""
        return self.bookings.filter(
            status__in=['approved', 'checked_in']
        ).select_related('guest').first()
    
    def update_status(self, new_status):
        """Update room status."""
        valid_transitions = {
            'available': ['reserved', 'maintenance'],
            'reserved': ['occupied', 'available', 'cancelled'],
            'occupied': ['available', 'maintenance'],
            'maintenance': ['available'],
        }
        
        if new_status in valid_transitions.get(self.status, []):
            self.status = new_status
            self.save()
            return True
        return False
    
    @classmethod
    def get_available_rooms(cls, check_in=None, check_out=None, room_type=None):
        """Get available rooms with optional filters."""
        from django.db.models import Q
        
        # Start with active available rooms
        queryset = cls.objects.filter(
            is_active=True,
            status='available'
        )
        
        # Filter by room type
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        # Exclude rooms with conflicting bookings
        if check_in and check_out:
            from apps.bookings.models import Booking
            conflicting_bookings = Booking.objects.filter(
                Q(status__in=['pending', 'approved', 'checked_in']) &
                Q(check_in__lt=check_out) &
                Q(check_out__gt=check_in)
            ).values_list('room_id', flat=True)
            
            queryset = queryset.exclude(id__in=conflicting_bookings)
        
        return queryset.select_related()


class RoomImage(models.Model):
    """
    Additional room images.
    """
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='rooms/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'room_images'
        verbose_name = 'Room Image'
        verbose_name_plural = 'Room Images'
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.room.room_number}"