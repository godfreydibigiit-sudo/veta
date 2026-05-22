"""
Admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from apps.users.models import User, StaffProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin with role-based fields."""
    
    list_display = [
        'email', 'full_name_display', 'phone', 'role_display',
        'position', 'is_active', 'is_staff_active', 'date_joined'
    ]
    
    list_filter = [
        'role', 'is_active', 'is_staff_active', 'is_staff',
        'department', 'position', 'date_joined'
    ]
    
    search_fields = [
        'email', 'phone', 'first_name', 'last_name',
        'staff_id', 'position', 'department'
    ]
    
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Login Information', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone', 'address', 'date_of_birth')
        }),
        ('Role & Permissions', {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser',
                'is_staff_active', 'position', 'department', 'staff_id'
            ),
        }),
        ('Staff Permissions', {
            'fields': (
                'can_manage_rooms', 'can_manage_bookings',
                'can_process_payments', 'can_check_in_out',
                'can_manage_staff', 'can_view_reports'
            ),
            'classes': ('collapse',),
            'description': 'Specific permissions for staff members. Managers and admins automatically have all permissions.'
        }),
        ('Security & Tracking', {
            'fields': ('last_login_ip', 'login_count', 'password_changed_at'),
            'classes': ('collapse',),
        }),
        ('Account Status', {
            'fields': ('is_verified', 'deactivated_at', 'deactivation_reason'),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'phone',
                'role', 'position', 'department',
                'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip', 'login_count']
    
    def get_fieldsets(self, request, obj=None):
        """
        Customize fieldsets based on user role.
        Managers and admins see all fields.
        """
        fieldsets = super().get_fieldsets(request, obj)
        
        if obj and obj.role == 'guest':
            # Remove staff-specific fields for guests
            return (
                ('Login Information', {
                    'fields': ('email', 'password')
                }),
                ('Personal Information', {
                    'fields': ('first_name', 'last_name', 'phone', 'address', 'date_of_birth')
                }),
                ('Role & Status', {
                    'fields': ('role', 'is_active'),
                }),
                ('Important Dates', {
                    'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
                    'classes': ('collapse',),
                }),
            )
        
        return fieldsets
    
    def full_name_display(self, obj):
        """Display full name with role badge."""
        name = obj.get_full_name() or obj.email
        if obj.role == 'admin':
            return format_html('<span style="color: #dc2626;">●</span> {}', name)
        elif obj.role == 'manager':
            return format_html('<span style="color: #7c3aed;">●</span> {}', name)
        elif obj.role == 'staff':
            return format_html('<span style="color: #2563eb;">●</span> {}', name)
        else:
            return format_html('<span style="color: #16a34a;">●</span> {}', name)
    full_name_display.short_description = 'Name'
    full_name_display.admin_order_field = 'first_name'
    
    def role_display(self, obj):
        """Display role with color coding."""
        colors = {
            'admin': ('#dc2626', 'Admin'),
            'manager': ('#7c3aed', 'Manager'),
            'staff': ('#2563eb', 'Staff'),
            'guest': ('#16a34a', 'Guest'),
        }
        color, label = colors.get(obj.role, ('#6b7280', obj.role))
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color, label
        )
    role_display.short_description = 'Role'
    role_display.admin_order_field = 'role'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('staff_profile')
    
    def save_model(self, request, obj, form, change):
        """Override save to handle staff profile and permissions."""
        # If user is manager or admin, grant all permissions
        if obj.role in ['manager', 'admin']:
            obj.can_manage_rooms = True
            obj.can_manage_bookings = True
            obj.can_process_payments = True
            obj.can_check_in_out = True
            obj.can_manage_staff = True
            obj.can_view_reports = True
            obj.is_staff_active = True
        
        super().save_model(request, obj, form, change)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    """Admin for staff profiles."""
    
    list_display = [
        'user', 'shift_display', 'hire_date',
        'emergency_contact_name', 'emergency_contact_phone'
    ]
    
    list_filter = [
        'shift', 'hire_date'
    ]
    
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'emergency_contact_name', 'emergency_contact_phone'
    ]
    
    fieldsets = (
        ('Staff Member', {
            'fields': ('user',)
        }),
        ('Work Information', {
            'fields': ('shift', 'hire_date', 'employee_notes')
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_phone',
                'emergency_contact_relation'
            )
        }),
    )
    
    raw_id_fields = ['user']
    
    def shift_display(self, obj):
        """Display shift with color."""
        colors = {
            'morning': '#f59e0b',
            'afternoon': '#3b82f6',
            'night': '#6366f1',
            'flexible': '#10b981',
        }
        color = colors.get(obj.shift, '#6b7280')
        shift_text = obj.get_shift_display()
        return format_html(
            '<span style="color: {}; font-weight: 500;">{}</span>',
            color, shift_text
        )
    shift_display.short_description = 'Shift'
    shift_display.admin_order_field = 'shift'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user')