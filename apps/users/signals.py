"""
Signals for user management.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User, StaffProfile


@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    """Create staff profile when staff user is created."""
    if created and instance.role in ['staff', 'admin']:
        StaffProfile.objects.get_or_create(user=instance)