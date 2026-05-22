"""
Base abstract models for the VETA Hotel Booking System.
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    Abstract base model for soft deletion.
    Instead of deleting records, they are marked as inactive.
    """
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Soft delete the record"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        """Restore a soft-deleted record"""
        self.is_active = True
        self.deleted_at = None
        self.save()


class AuditLog(models.Model):
    """
    Audit log to track all financial and sensitive operations.
    Prevents fraud by maintaining immutable records.
    """
    ACTION_CHOICES = [
        ('payment_received', 'Payment Received'),
        ('payment_refunded', 'Payment Refunded'),
        ('booking_approved', 'Booking Approved'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('check_in', 'Guest Check-in'),
        ('check_out', 'Guest Check-out'),
        ('room_status_changed', 'Room Status Changed'),
        ('staff_created', 'Staff Created'),
        ('staff_deactivated', 'Staff Deactivated'),
        ('price_changed', 'Room Price Changed'),
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    
    def __str__(self):
        return f"{self.get_action_display()} by {self.user.get_full_name()} at {self.created_at}"        
