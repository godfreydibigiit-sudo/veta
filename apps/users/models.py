"""
User models for VETA Hotel Booking System.
Custom User model with role-based authentication and permissions.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    Provides helper methods for querying users by role.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with email and password.
        Default role is 'guest' if not specified.
        """
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'guest')
        extra_fields.setdefault('is_active', True)
        
        # Generate username from email if not provided
        if not extra_fields.get('username'):
            extra_fields['username'] = email
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with full permissions.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)
    
    def create_staff(self, email, password=None, **extra_fields):
        """
        Create a staff member account.
        """
        extra_fields.setdefault('role', 'staff')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff_active', True)
        return self.create_user(email, password, **extra_fields)
    
    def create_manager(self, email, password=None, **extra_fields):
        """
        Create a hotel manager account.
        """
        extra_fields.setdefault('role', 'manager')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff_active', True)
        return self.create_user(email, password, **extra_fields)
    
    def guests(self):
        """Return all active guest users."""
        return self.filter(role='guest', is_active=True)
    
    def staff_members(self):
        """Return all active staff members (excluding managers and admins)."""
        return self.filter(role='staff', is_active=True, is_staff_active=True)
    
    def managers(self):
        """Return all active hotel managers."""
        return self.filter(role='manager', is_active=True, is_staff_active=True)
    
    def hotel_employees(self):
        """Return all active hotel employees (staff, managers, admins)."""
        return self.filter(
            role__in=['staff', 'manager', 'admin'],
            is_active=True,
            is_staff_active=True
        )
    
    def admins(self):
        """Return all admin users."""
        return self.filter(role='admin', is_active=True)


class User(AbstractUser, TimeStampedModel):
    """
    Custom User model with role-based access control.
    
    Roles:
        - guest: Regular hotel guest (can browse and book rooms)
        - staff: Hotel staff (can manage bookings, check-ins, payments)
        - manager: Hotel manager (full hotel oversight, can manage staff)
        - admin: System administrator (full system access)
    
    Authentication uses email instead of username.
    """
    
    class Role(models.TextChoices):
        GUEST = 'guest', 'Guest'
        STAFF = 'staff', 'Staff'
        MANAGER = 'manager', 'Hotel Manager'
        ADMIN = 'admin', 'Admin'
    
    # Override username to make it optional (we use email for auth)
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text="Auto-generated from email if not provided"
    )
    
    # Required fields
    email = models.EmailField(
        'email address',
        unique=True,
        db_index=True,
        error_messages={
            'unique': "A user with this email already exists.",
        }
    )
    
    phone = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        help_text="Format: +255712345678 or 0712345678"
    )
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.GUEST,
        db_index=True,
        help_text="User role determines access permissions"
    )
    
    # Personal Information
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        help_text="Optional profile picture"
    )
    address = models.TextField(
        blank=True,
        verbose_name='Physical Address',
        help_text="Guest address (optional)"
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date of Birth'
    )
    
    # Staff-specific Information
    staff_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Employee ID',
        help_text="Internal staff identification number"
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Job Title',
        help_text="Staff position or job title"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Department or section"
    )
    is_staff_active = models.BooleanField(
        default=True,
        verbose_name='Staff Account Active',
        help_text="Designates whether this staff member can access the system"
    )
    
    # Permissions (for staff/manager roles)
    can_manage_rooms = models.BooleanField(
        default=False,
        help_text="Can add, edit, and delete rooms"
    )
    can_manage_bookings = models.BooleanField(
        default=False,
        help_text="Can approve, cancel, and manage bookings"
    )
    can_process_payments = models.BooleanField(
        default=False,
        help_text="Can process and record payments"
    )
    can_check_in_out = models.BooleanField(
        default=False,
        help_text="Can check guests in and out"
    )
    can_manage_staff = models.BooleanField(
        default=False,
        help_text="Can create and manage staff accounts"
    )
    can_view_reports = models.BooleanField(
        default=False,
        help_text="Can view financial and operational reports"
    )
    
    # Security & Tracking
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Last Login IP'
    )
    login_count = models.IntegerField(
        default=0,
        verbose_name='Total Logins'
    )
    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the password was last changed"
    )
    
    # Account Status
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the user's identity has been verified"
    )
    deactivated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the account was deactivated"
    )
    deactivation_reason = models.TextField(
        blank=True,
        help_text="Reason for account deactivation"
    )
    
    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
    
    def get_initials(self):
        """Return user initials for avatar display."""
        first = self.first_name[0] if self.first_name else ''
        last = self.last_name[0] if self.last_name else ''
        return f"{first}{last}".upper() or self.email[0].upper()
    
    # ============================================
    # ROLE CHECK METHODS
    # ============================================
    
    def is_guest(self):
        """Check if user is a guest."""
        return self.role == self.Role.GUEST
    
    def is_staff_member(self):
        """Check if user is a regular staff member."""
        return self.role == self.Role.STAFF
    
    def is_manager(self):
        """Check if user is a hotel manager."""
        return self.role == self.Role.MANAGER
    
    def is_admin(self):
        """Check if user is a system administrator."""
        return self.role == self.Role.ADMIN
    
    def is_staff_user(self):
        """
        Check if user has any staff-level access.
        Returns True for staff, managers, and admins.
        """
        return self.role in [self.Role.STAFF, self.Role.MANAGER, self.Role.ADMIN]
    
    def is_hotel_management(self):
        """
        Check if user is part of hotel management.
        Returns True for managers and admins.
        """
        return self.role in [self.Role.MANAGER, self.Role.ADMIN]
    
    # ============================================
    # PERMISSION METHODS
    # ============================================
    
    def has_permission(self, permission_name):
        """
        Check if user has a specific permission.
        Managers and admins automatically get all permissions.
        """
        if self.is_hotel_management():
            return True
        
        permission_map = {
            'manage_rooms': self.can_manage_rooms,
            'manage_bookings': self.can_manage_bookings,
            'process_payments': self.can_process_payments,
            'check_in_out': self.can_check_in_out,
            'manage_staff': self.can_manage_staff,
            'view_reports': self.can_view_reports,
        }
        return permission_map.get(permission_name, False)
    
    def get_permissions(self):
        """Return a dictionary of all permissions."""
        if self.is_hotel_management():
            return {
                'manage_rooms': True,
                'manage_bookings': True,
                'process_payments': True,
                'check_in_out': True,
                'manage_staff': True,
                'view_reports': True,
            }
        
        return {
            'manage_rooms': self.can_manage_rooms,
            'manage_bookings': self.can_manage_bookings,
            'process_payments': self.can_process_payments,
            'check_in_out': self.can_check_in_out,
            'manage_staff': self.can_manage_staff,
            'view_reports': self.can_view_reports,
        }
    
    # ============================================
    # ACCOUNT MANAGEMENT METHODS
    # ============================================
    
    def record_login(self, ip_address=None):
        """Record user login information."""
        self.last_login_ip = ip_address
        self.login_count += 1
        self.save(update_fields=['last_login_ip', 'login_count'])
    
    def deactivate(self, reason=''):
        """
        Deactivate this user account.
        """
        self.is_active = False
        self.is_staff_active = False
        self.deactivated_at = timezone.now()
        self.deactivation_reason = reason
        self.save(update_fields=[
            'is_active', 'is_staff_active',
            'deactivated_at', 'deactivation_reason'
        ])
    
    def activate(self):
        """
        Reactivate this user account.
        """
        self.is_active = True
        self.is_staff_active = True
        self.deactivated_at = None
        self.deactivation_reason = ''
        self.save(update_fields=[
            'is_active', 'is_staff_active',
            'deactivated_at', 'deactivation_reason'
        ])
    
    def set_permissions(self, permissions_dict):
        """
        Set staff permissions from a dictionary.
        Only applicable for staff role.
        """
        if self.is_hotel_management():
            return  # Managers and admins have all permissions
        
        for key, value in permissions_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
    
    # ============================================
    # RELATED DATA METHODS
    # ============================================
    
    def get_booking_history(self):
        """Get all bookings for this user."""
        return self.bookings.all().select_related('room')
    
    def get_active_booking(self):
        """Get current active booking if any."""
        return self.bookings.filter(
            status__in=['approved', 'checked_in']
        ).first()
    
    def get_recent_bookings(self, limit=5):
        """Get recent bookings for this user."""
        return self.bookings.select_related('room').order_by('-created_at')[:limit]
    
    def get_total_spent(self):
        """Calculate total amount spent by this guest."""
        from django.db.models import Sum
        result = self.bookings.filter(
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))
        return result['total'] or 0
    
    def get_full_address(self):
        """Return formatted full address."""
        parts = [self.get_full_name()]
        if self.address:
            parts.append(self.address)
        parts.append(f"Phone: {self.phone}")
        return "\n".join(parts)
    
    def to_dict(self):
        """Return a dictionary of basic user information."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.get_full_name(),
            'phone': self.phone,
            'role': self.role,
            'role_display': self.get_role_display(),
            'is_active': self.is_active,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None,
        }


class StaffProfile(models.Model):
    """
    Extended profile for staff members.
    Contains additional staff-specific information.
    """
    
    class Shift(models.TextChoices):
        MORNING = 'morning', 'Morning Shift (6AM - 2PM)'
        AFTERNOON = 'afternoon', 'Afternoon Shift (2PM - 10PM)'
        NIGHT = 'night', 'Night Shift (10PM - 6AM)'
        FLEXIBLE = 'flexible', 'Flexible Hours'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    
    # Emergency Contact
    emergency_contact_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Name of emergency contact person"
    )
    emergency_contact_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Emergency contact phone number"
    )
    emergency_contact_relation = models.CharField(
        max_length=50,
        blank=True,
        help_text="Relationship to emergency contact"
    )
    
    # Work Information
    shift = models.CharField(
        max_length=20,
        choices=Shift.choices,
        default=Shift.MORNING
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the staff member was hired"
    )
    employee_notes = models.TextField(
        blank=True,
        help_text="Internal notes about this staff member (not visible to them)"
    )
    
    class Meta:
        db_table = 'staff_profiles'
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'
    
    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"
    
    def get_shift_display_full(self):
        """Return full shift description."""
        return dict(self.Shift.choices).get(self.shift, self.shift)