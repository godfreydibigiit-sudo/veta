"""
Admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from apps.users.models import User, StaffProfile


class StaffProfileInline(admin.StackedInline):
    """Inline admin for staff profile."""
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile'
    fk_name = 'user'
    max_num = 1
    min_num = 0
    extra = 0  # Don't show extra empty forms


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin with role-based fields."""
    
    list_display = [
        'email', 'full_name_display', 'phone', 'role_display', 
        'is_active', 'date_joined'
    ]
    
    list_filter = [
        'role', 'is_active', 'is_staff', 'date_joined'
    ]
    
    search_fields = ['email', 'phone', 'first_name', 'last_name']
    
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Login Information', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone', 'address', 'date_of_birth')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'position', 'staff_id'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'phone',
                'role', 'position', 'password1', 'password2'
            ),
        }),
    )
    
    # Only show StaffProfileInline for existing users, not when adding
    def get_inlines(self, request, obj=None):
        """Don't show inlines when adding a new user."""
        if obj:  # Only show when editing existing user
            return [StaffProfileInline]
        return []
    
    def full_name_display(self, obj):
        """Display full name with role badge."""
        name = obj.get_full_name() or obj.email
        if obj.role == 'admin':
            return format_html('<span style="color: red;">●</span> {}', name)
        elif obj.role == 'staff':
            return format_html('<span style="color: blue;">●</span> {}', name)
        else:
            return format_html('<span style="color: green;">●</span> {}', name)
    full_name_display.short_description = 'Name'
    full_name_display.admin_order_field = 'first_name'
    
    def role_display(self, obj):
        """Display role with color."""
        colors = {
            'admin': ('red', 'Admin'),
            'staff': ('blue', 'Staff'),
            'guest': ('green', 'Guest'),
        }
        color, label = colors.get(obj.role, ('gray', obj.role))
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color, label
        )
    role_display.short_description = 'Role'
    role_display.admin_order_field = 'role'
    
    def save_model(self, request, obj, form, change):
        """Override save to handle staff profile creation."""
        super().save_model(request, obj, form, change)
        # Create staff profile after saving if user is staff/admin
        if obj.role in ['staff', 'admin']:
            StaffProfile.objects.get_or_create(user=obj)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    """Admin for staff profiles."""
    
    list_display = [
        'user', 'department', 'shift', 
        'can_manage_bookings', 'can_process_payments'
    ]
    
    list_filter = ['department', 'shift', 'can_manage_bookings', 'can_process_payments']
    
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'department']
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('user', 'department', 'emergency_contact', 'shift')
        }),
        ('Permissions', {
            'fields': (
                'can_manage_rooms', 'can_manage_bookings',
                'can_process_payments', 'can_check_in_out'
            )
        }),
    )