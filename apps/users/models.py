"""
User models for VETA Hotel Booking System.
Custom User model with role-based authentication.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.core.constants import USER_ROLES


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with email and password."""
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)
    
    def staff_users(self):
        """Return all staff and admin users."""
        return self.filter(role__in=['staff', 'admin'], is_active=True)
    
    def guest_users(self):
        """Return all guest users."""
        return self.filter(role='guest', is_active=True)


class User(AbstractUser, TimeStampedModel):
    """
    Custom User model with role-based access.
    Login with email instead of username.
    """
    ROLE_CHOICES = USER_ROLES
    
    # Override username to make it optional
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    # Required fields
    email = models.EmailField('email address', unique=True, db_index=True)
    phone = models.CharField(
        max_length=15, 
        unique=True, 
        db_index=True,
        help_text="Enter phone number in format: +255712345678 or 0712345678"
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='guest',
        db_index=True
    )
    
    # Additional fields
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True,
        help_text="Optional profile picture"
    )
    address = models.TextField(blank=True, help_text="Guest address (optional)")
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Staff-specific fields
    staff_id = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        unique=True,
        help_text="Staff ID for internal reference"
    )
    position = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Staff position/title"
    )
    is_staff_active = models.BooleanField(
        default=True,
        help_text="Designates whether staff can access the system"
    )
    
    # Login tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    login_count = models.IntegerField(default=0)
    
    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
    
    def is_staff_user(self):
        """Check if user has staff or admin role."""
        return self.role in ['staff', 'admin']
    
    def is_guest_user(self):
        """Check if user has guest role."""
        return self.role == 'guest'
    
    def get_full_address(self):
        """Return formatted full address."""
        if self.address:
            return f"{self.get_full_name()}\n{self.address}\nPhone: {self.phone}"
        return f"{self.get_full_name()}\nPhone: {self.phone}"
    
    def record_login(self, ip_address=None):
        """Record user login information."""
        self.last_login_ip = ip_address
        self.login_count += 1
        self.save(update_fields=['last_login_ip', 'login_count'])
    
    def get_booking_history(self):
        """Get all bookings for this user."""
        return self.bookings.all().select_related('room')
    
    def get_active_booking(self):
        """Get current active booking if any."""
        return self.bookings.filter(
            status__in=['approved', 'checked_in']
        ).first()


class StaffProfile(models.Model):
    """
    Extended profile for staff members.
    Contains additional staff-specific information.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='staff_profile'
    )
    department = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    shift = models.CharField(
        max_length=20,
        choices=[
            ('morning', 'Morning Shift'),
            ('afternoon', 'Afternoon Shift'),
            ('night', 'Night Shift'),
        ],
        default='morning'
    )
    can_manage_rooms = models.BooleanField(default=False)
    can_manage_bookings = models.BooleanField(default=True)
    can_process_payments = models.BooleanField(default=False)
    can_check_in_out = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'staff_profiles'
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'
    
    def __str__(self):
        return f"Staff Profile: {self.user.get_full_name()}"